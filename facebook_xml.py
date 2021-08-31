import argparse
import xml.etree.ElementTree as ET

from daily_functions import get_brand, get_connection

header = """
<?xml version="1.0"?>
<rss xmlns:g="http://base.google.com/ns/1.0" version="2.0">
<channel>
<title>Корейская косметика</title>
<link>https://beautyty.org</link>
<description>Качественная косетика из Кореи</description>
"""

footer = """
</channel>
</rss>
"""

item_template = """
<item>
    <g:id>{good_id}</g:id>
    <g:title>{title}</g:title>
    <g:description>{text_description}</g:description>
    <g:rich_text_description><![CDATA[{html_description}]]></g:rich_text_description>
    <g:link>{link}</g:link>
    <g:image_link>{img_url}</g:image_link>
    <g:brand>{brand}</g:brand>
    <g:condition>new</g:condition>
    <g:availability>in stock</g:availability>
    <g:price>{price} RUB</g:price>
    <g:google_product_category>Health &amp; Beauty > Personal Care > Cosmetics</g:google_product_category>
    <g:custom_label_0>Корейская косметика 🇰🇷</g:custom_label_0>
</item>
"""

tree = ET.parse('feed-yml-0.xml')
root = tree.getroot()

ads_items = ''

total_count = 0
key_words_idx = 0


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

            for child in item:
                tag_name = child.tag

                if tag_name == 'name':
                    title = child.text.replace('&', '&amp;')
                elif tag_name == 'description':
                    text = child.text.replace('&', '&amp;')
                    text_description = text
                    html_description = make_description(text)
                elif tag_name == 'price':
                    price = int(float(child.text))
                elif tag_name == 'picture':
                    img_url = child.text
                elif tag_name == 'url':
                    url = child.text

            if price < 999:
                continue

            brand = get_brand(good_id, connection)
            ad_item = item_template.format(
                good_id=good_id,
                title=title,
                text_description=text_description,
                html_description=html_description,
                link=url,
                img_url=img_url,
                brand=brand,
                price=price,
            )

            ads_items += ad_item

        key_words_idx += 1

    xml_final = header + ads_items + footer

    with open('facebook.xml', 'w') as f:
        f.write(xml_final)
        f.flush()
