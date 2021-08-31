import xml.etree.ElementTree as ET

import xlrd

from daily_functions import get_clear_title


def parse_xml():
    tree = ET.parse('feed-yml-0.xml')
    root = tree.getroot()

    names_dict_first = {}
    names_dict_second = {}

    for item in root.iter('offer'):
        item_attrs = item.attrib
        if 'available' in item_attrs:
            for child in item:
                tag_name = child.tag

                if tag_name == 'name':
                    title = child.text
                    words = title.split(' ')
                    names_dict_first.setdefault(words[0], 0)
                    names_dict_second.setdefault(words[1], 0)

                    names_dict_first[words[0]] += 1
                    names_dict_second[words[1]] += 1


    print(len(names_dict_first))
    print(len(names_dict_second))

    print(names_dict_first)
    print(names_dict_second)


def find_price_coefficient():
    xl = xlrd.open_workbook('Prays-list optovyiy KEAUTY 092019.xls (1).xlsx')
    sheet_1 = xl.sheet_by_index(0)

    prices_ratio = set()

    for i, rownum in enumerate(range(sheet_1.nrows)):
        if i < 12:
            continue

        row = sheet_1.row_values(rownum)
        if not row[1] or row[1] == 'Штрихкод':
            continue

        price_30k = None
        price = None
        title = None

        for col_idx, c_el in enumerate(row):
            if col_idx == 6:
                title = c_el
            if col_idx == 10:
                try:
                    price_30k = float(c_el)
                except Exception as e:
                    print(c_el)
                    print(e)
                    break
            if col_idx == 11:
                try:
                    price = float(c_el)
                except Exception as e:
                    print(c_el)
                    print(e)
                    break

        if price is None or price_30k is None:
            print('Problem with good: {}'.format(title))
            continue
        ratio = round(price / price_30k, 2)
        prices_ratio.add(ratio)

    print(sorted(prices_ratio, reverse=True))


if __name__ == '__main__':
    find_price_coefficient()