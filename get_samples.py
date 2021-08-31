import argparse

import requests
import xlrd

import brands_map
from brands_map import brands_list
from daily_functions import get_connection, get_clear_title

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('--db', help='Use database')
    parser.add_argument('--port', help='Database port')
    parser.add_argument('--date', help='File last update date')

    args = parser.parse_args()

    database_name = args.db
    database_port = args.port
    date = args.date

    connection = get_connection(database_name, database_port)
    cursor = connection.cursor()
    """
    0 Штрихкод	
    1 Артикул	
    2 Место нанесения	
    3 Действие	
    4 Изображение	
    5 Номенклатура	
    6 вес(объем)	
    7 Акция	
    8 Остаток	Заказ	
    9 ОПТ от  300 000 руб	
    10 ОПТ от 100 000 руб	
    11 ОПТ от 30 000 руб	
    12 Розничные	
    13 Сумма	
    14 Описание															
    """

    rb = xlrd.open_workbook('Blank zakaza {}.xlsx'.format(date))
    sheet = rb.sheet_by_index(0)

    start_row = 16
    set_goods = set()
    goods_cnt = 0
    row_numb = 0
    errors_dict = {}

    with open('samples.csv', 'w') as f:
        for i, rownum in enumerate(range(sheet.nrows), start=1):
            if i < start_row:
                continue

            row = sheet.row_values(rownum)
            if not row[1] or row[1] == 'Штрихкод':
                continue

            rubric_1 = None
            rubric_2 = None
            price = None
            price_30k = None
            scan_code = None
            title = None
            description = None

            categ_1 = None
            categ_2 = None

            info = None

            for col_idx, c_el in enumerate(row):
                if col_idx == 1:
                    scan_code = int(float(c_el))
                if col_idx == 3:
                    categ_1 = c_el
                if col_idx == 4:
                    categ_2 = c_el
                elif col_idx == 6:
                    title = c_el
                    title = title.replace('"', "'")
                    try:
                        brand = brands_map.brands_map[title.split(' ')[0]]
                    except KeyError:
                        errors_dict.setdefault(title.split(' ')[0], 0)
                        errors_dict[title.split(' ')[0]] += 1
                        brand = None
                    title = get_clear_title(title) or title
                elif col_idx == 8:
                    info = c_el
                elif col_idx == 13:
                    try:
                        price_30k = int(float(c_el))
                    except ValueError:
                        print('Value error price30k: {i}: price: {price}'.format(i=i, price=c_el))

            if not brand:
                continue

            is_sample = False

            if 'пробн' in info.lower():
                is_sample = True

            if 'пробн'in title.lower():
                is_sample = True

            if 'sample'in title.lower():
                is_sample = True

            if not is_sample:
                continue

            url_1 = 'https://beautyty.org/wp-content/uploads/2019/01/{}.jpg'.format(scan_code)
            url_2 = 'https://beautyty.org/wp-content/uploads/2019/01/{}_1.jpg'.format(scan_code)

            response_1 = requests.get(url_1)
            response_2 = requests.get(url_2)

            if response_1.status_code == 200:
                url = url_1
            elif response_2.status_code == 200:
                url = url_2
            else:
                url = None

            title = title.replace(brand, '')
            row_numb += 1
            f.write('"{row_numb}"; "{brand} {title}"; '
                    '"{scan_code}"; "{brand}"; "{price_30k}";'
                    '"{url}"\n'.format(
                row_numb=row_numb,
                title=title,
                scan_code=scan_code,
                brand=brand,
                url=url,
                price_30k=price_30k
            ))

    print(errors_dict)