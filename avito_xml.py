import xml.etree.ElementTree as ET

ad_template = """
   <Ad>
        <Id>{good_id}</Id>
        <DateBegin>{date_begin}</DateBegin>
        <DateEnd>{date_end}</DateEnd>
        <AllowEmail>Да</AllowEmail>
        <ManagerName>Илья</ManagerName>
        <ContactPhone>+7 925 074-58-96</ContactPhone>
        <Region>Москва</Region>
        <City>Москва</City>
        <Category>Красота и здоровье</Category>
        <GoodsType>Косметика</GoodsType>
		<AdType>Товар от производителя</AdType>
        <Title>{title}</Title>
      <Description><![CDATA[{description}]]></Description>
        <Price>{price}</Price>
        <Images>
            <Image url="{img_url}" />
        </Images>
    </Ad>
"""

tree = ET.parse('feed-yml-0.xml')
root = tree.getroot()

ads_items = ''

key_words = (
    ('патчи', 'Патчи'),
    ('крем для лица', 'Крем для лица'),
    ('ББ-крем', 'ББ крем'),
    ('ВВ-крем', 'ВВ крем'),
    ('СС-крем', 'СС крем'),
    ('BB-крем', 'BB крем'),
    ('CC-крем', 'CC крем'),
    ('Шампунь', 'шампунь'),
    ('Тинт', 'тинт'),
    ('Тушь', 'тушь'),
    ('Маска', 'маска'),
    ('Эмульсия', 'эмульсия'),
    ('Пенка', 'пенка'),
    ('Масло', 'масло'),
    ('Кушон', 'кушон'),
    ('Пилинг', 'пилинг'),
    ('Комплект', 'комплект'),
    ('Скраб', 'скраб'),

    ('пудра', 'Пудра'),
)

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

while total_count < 100:
    for item in root.iter('offer'):
        item_attrs = item.attrib
        if 'available' in item_attrs:
            if item_attrs['available'] == 'false':
                continue

            good_id = item_attrs['id']
            title = None
            description = None
            price = None
            img_url = None

            for child in item:
                tag_name = child.tag

                if tag_name == 'name':
                    title = child.text
                elif tag_name == 'description':
                    description = make_description(child.text)
                elif tag_name == 'price':
                    price = int(float(child.text))
                elif tag_name == 'picture':
                    img_url = child.text

            if key_words[key_words_idx][0] not in title and key_words[key_words_idx][1] not in title:
                continue

            if price < 999:
                continue

            ad_item = ad_template.format(
                good_id=good_id,
                title=title,
                description=description,
                date_begin='28-12-2019',
                date_end='29-01-2020',
                price=price,
                img_url=img_url
            )

            ads_items += ad_item
            total_count += 1

            if total_count > 100:
                break

    key_words_idx += 1

xml_final = '<Ads formatVersion="3" target="Avito.ru">' + ads_items + '</Ads>'

with open('avito.xml', 'w') as f:
    f.write(xml_final)
    f.flush()
