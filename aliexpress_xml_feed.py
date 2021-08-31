import argparse
import xml.etree.ElementTree as ET

from daily_functions import get_brand, get_connection, get_good_categories

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
<categories>
<category id="200">Крем для лица</category>
<category id="201">Тонер</category>
<category id="202">Масло для лица</category>
<category id="203">Маска для лица</category>
<category id="204">Сыворотка для лица</category>
<category id="205">Эмульсия для лица</category>
</categories>
<offers>
"""

cat_id = 205

footer = """</offers>
</shop>
</yml_catalog>
"""

item_template = """<offer  id="{good_id}" available="true" >
<name>{title}</name>
<picture>{img_url}</picture>
<url>{url}</url>
<price>{price}.0</price>
<sale_price>{sale_price}.0</sale_price>
<description>{description}</description>
<brand>{brand}</brand>
<currencyId>RUR</currencyId>
<categoryId>{cat_id}</categoryId>
<store>false</store>
<pickup>false</pickup>
<delivery>true</delivery>
<size>small</size>
<count>10</count>
<color>#FFFFFF</color>
</offer>
"""

tree = ET.parse('feed-yml-0.xml')
root = tree.getroot()

ads_items = ''

total_count = 0

def make_description(text):
    final_text = ''
    buf_text = ''
    for idx, sentence in enumerate(text.split('.')):
        buf_text += sentence + '.'
        if idx != 0 and idx % 2 == 0:
            final_text += '<p>{buf_text}</p>'.format(buf_text=buf_text)
            buf_text = ''

    return final_text

parser = argparse.ArgumentParser()
parser.add_argument('--db', help='Use database')
parser.add_argument('--port', help='Database port')

args = parser.parse_args()
database_name = args.db
database_port = args.port

if __name__ == '__main__':
    connection = get_connection(database_name, database_port)

    for item in root.iter('offer'):
        item_attrs = item.attrib
        if 'available' in item_attrs:
            if item_attrs['available'] == 'false':
                continue

            good_id = item_attrs['id']
            title = None
            text_description = None
            html_description = None
            price = None
            img_url = None
            url = None
            sale_price = None

            for child in item:
                tag_name = child.tag

                if tag_name == 'name':
                    title = child.text.replace('&', '&amp;')
                elif tag_name == 'description':
                    text = child.text.replace('&', '&amp;')
                    text_description = text
                    html_description = make_description(text)
                elif tag_name == 'price':
                    sale_price = int(float(child.text))
                    price = int(1.4 * sale_price)
                elif tag_name == 'picture':
                    img_url = child.text
                elif tag_name == 'url':
                    url = child.text


            if price < 700:
                continue

            is_need_category = False
            for cat in get_good_categories(good_id, connection):
                if cat[2] == 'Лицо':
                    is_need_category = True

            if not is_need_category:
                continue

            brand = get_brand(good_id, connection)

            if 'эмульсия' in title.lower():

                ad_item = item_template.format(
                    good_id=good_id,
                    title=title,
                    description=text_description,
                    #html_description=html_description,
                    url=url,
                    img_url=img_url,
                    brand=brand,
                    sale_price=sale_price,
                    price=price,
                    cat_id=cat_id
                )

                ads_items += ad_item

    xml_final = header + ads_items + footer

    with open('ali_express.xml', 'w') as f:
        f.write(xml_final)
        f.flush()
