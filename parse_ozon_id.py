import argparse
from time import sleep

import requests
from lxml import html
from daily_functions import get_connection, get_price_by_id

parser = argparse.ArgumentParser()
parser.add_argument('--db', help='Use database')
parser.add_argument('--port', help='Database port')

args = parser.parse_args()
database_name = args.db
database_port = args.port


connection = get_connection(database_name, database_port)
cursor = connection.cursor()

cursor.execute("select ID, post_title from wp_posts WHERE ID > 70 and post_type='product' ORDER BY  ID DESC")

ozon_map = {}
not_found_cnt = 0
errors_cnt = 0
found_cnt = 0

for row in cursor.fetchall():
    product_id = row[0]
    title = row[1]

    ozon_url = 'https://www.ozon.ru/search/?text={title}&from_global=true'

    headers = requests.utils.default_headers()
    headers.update(
        {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
        }
    )

    sleep(0.5)
    response = requests.get(url=ozon_url.format(title=title), headers=headers)

    tree = html.fromstring(response.text)

    tags = tree.xpath('//a[@class="a0m3"]')

    if len(tags) == 0:
        not_found_cnt += 1
        print('Not found: {}'.format(title))
        continue

    try:
        ozon_id = tags[0].attrib['href'].split('/')[-2]
    except Exception:
        errors_cnt += 1
        print('Error: {}'.format(title))
        continue
    else:
        found_cnt += 1
        ozon_map[product_id] = ozon_id

row_numb = 0
with open('ozon_map.csv', 'w') as f:
    for key, value in ozon_map.items():
        price = get_price_by_id(key, connection)
        row_numb += 1
        f.write('{row_numb}; {product_id}; {ozon_id}; {price}; {before_price};\n'.format(
            row_numb=row_numb,
            product_id=key,
            ozon_id=value,
            price=int(price),
            before_price=int(price*1.4)
        ))

print('Not found in ozon: {}'.format(not_found_cnt))
print('Errors while parsing: {}'.format(errors_cnt))
print('Parse ozon ids: {}'.format(found_cnt))