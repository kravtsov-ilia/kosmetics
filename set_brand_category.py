import argparse

import xlrd
from mysql.connector import InternalError

import brands_map
from daily_functions import get_connection, get_good_id_by_title, set_brand_category, get_clear_title

rubrics = set()

start_row = 16

set_goods = set()
goods_cnt = 0

parser = argparse.ArgumentParser()
parser.add_argument('--db', help='Use database')
parser.add_argument('--port', help='Database port')

args = parser.parse_args()
database_name = args.db
database_port = args.port

connection = get_connection(database_name, database_port)
cursor = connection.cursor()
counter = 0

rb = xlrd.open_workbook('Prays-list optovyiy KEAUTY 092019.xls (1).xlsx')
sheet = rb.sheet_by_index(0)

for i, rownum in enumerate(range(sheet.nrows)):
    if i < start_row:
        continue

    row = sheet.row_values(rownum)
    if not row[1] or row[1] == 'Штрихкод':
        continue

    brand_category = None
    title = None
    brand = None

    for col_idx, c_el in enumerate(row):

        if col_idx == 6:
            title = c_el
            title = title.replace('"', "'")
            brand = title.split(' ')[0]
            brand_category = brands_map.brands_map.get(brand)
            title = get_clear_title(title)
            break

    if not brand_category:
        print('Brand not found: {}'.format(brand))
        continue
    try:
        good_obj = get_good_id_by_title(title, connection)
    except InternalError as e:
        print(e)
    else:
        if good_obj and len(good_obj) > 0:
            good_id = good_obj[0]
            print('i = {0}; brand_category = {1}; title = {2};'.format(i, brand_category, title))
            set_brand_category(good_id, brand_category, connection)


print(counter)