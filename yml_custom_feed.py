import argparse

from daily_functions import get_connection, get_all_goods, get_image_by_id, get_product_url, get_price_by_id, \
    get_barcode, get_categories, get_category, get_stock_status, get_product_description_by_id, get_brand

goods_cnt = 0

parser = argparse.ArgumentParser()
parser.add_argument('--db', help='Use database')
parser.add_argument('--port', help='Database port')
parser.add_argument('--path', help='Path to result file')

args = parser.parse_args()
database_name = args.db
database_port = args.port
result_path = args.path

connection = get_connection(database_name, database_port)
cursor = connection.cursor()

header = """<?xml version="1.0" encoding="UTF-8"?>
<yml_catalog date="2020-01-28 16:12">
<shop>
<name>🇰🇷 Корейская косметика</name>
<company>🇰🇷 Корейская косметика</company>
<url>https://beautyty.org/</url>
<platform>WordPress - Yml for Yandex Market</platform>
<version>5.2.5</version>
<currencies>
<currency id="RUR" rate="1"/>
</currencies>
<categories>"""

categorie_template = """<category id="{category_id}">{category_name}</category>\n"""

categories_close_block = """</categories>
<offers>"""

offer_template = """
<offer  id="{product_id}" available="true" >
<name>{title}</name>
<description>{description}</description>
<vendor>{brand}</vendor>
<picture>{picture}</picture>
<url>{url}</url>
<price>{price}.0</price>
<oldprice>{old_price}.0</oldprice>
<barcode>{barcode}</barcode>
<vendorCode>{barcode}</vendorCode>
<weight>{weight}</weight>
<dimensions>{long}/{width}/{height}</dimensions>
<currencyId>RUR</currencyId>
<store>false</store>
<pickup>false</pickup>
<delivery>true</delivery>
<categoryId>{category_id}</categoryId>
</offer>
"""

footer = """</offers>
</shop>
</yml_catalog>"""

categories = get_categories(connection)

categories_block = ''
for categ in categories:
    categories_block += categorie_template.format(
        category_id=categ[0],
        category_name=categ[1]
    )

offers_block = ''

for good in get_all_goods(connection):
    post_id = good[0]
    title = good[1]

    stock_status = get_stock_status(post_id, connection)

    if stock_status[0] != 'instock':
        print('Product not in stock: {}'.format(post_id))
        continue

    picture = get_image_by_id(post_id, connection)

    if 'beautyty.orgwp-content' in picture:
        picture = picture.replace('beautyty.orgwp-content', 'beautyty.org/wp-content')
    elif 'http://localhost/wp' in picture:
        picture = picture.replace('http://localhost/wp', 'https://beautyty.org')

    url = get_product_url(post_id, connection)

    raw_price = None
    try:
        raw_price = get_price_by_id(post_id, connection)
        price = int(float(raw_price))
    except ValueError:
        print('Error price: {}. Post id: {}'.format(raw_price, post_id))
        continue

    if price < 700:
        continue

    description = get_product_description_by_id(post_id, connection)
    brand = get_brand(post_id,connection)
    if not brand:
        print('Brand not found: {}'.format(post_id))
        continue

    old_price = int(1.4*price)

    barcode = get_barcode(post_id, connection)

    weight = 0.350

    long = 20
    width = 20
    height = 13

    product_category = get_category(post_id, connection)
    product_category_id = None

    categories_part = ''
    for categ in categories:
        categories_part += categorie_template.format(category_id=categ[0], category_name=categ[1])
        if categ[1] == product_category:
            product_category_id = categ[0]

    if not product_category_id:
        print('No category id: {}'.format(post_id))
        continue

    offers_block += offer_template.format(
        product_id=post_id,
        title='<![CDATA[{} {}]]>'.format(brand, title),
        brand=brand,
        description='<![CDATA[{}]]>'.format(description),
        picture=picture,
        url=url,
        price=price,
        old_price=old_price,
        barcode=barcode,
        weight=weight,
        long=long,
        width=width,
        height=height,
        category_id=product_category_id,
    )

with open('{}/new_yml_feed.xml'.format(result_path), 'w') as f:
    feed = header + categories_block + categories_close_block + offers_block + footer
    f.write(feed)
