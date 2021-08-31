import argparse

import xlrd
from mysql.connector import InternalError

from daily_functions import get_connection, get_good_id_by_title, get_good_categories, set_categories_for_good

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

    rubric_1 = None
    rubric_2 = None
    price = None
    scan_code = None
    title = None

    for col_idx, c_el in enumerate(row):
        if col_idx == 3:
            rubric_1 = c_el
        elif col_idx == 4:
            rubric_2 = c_el
        elif col_idx == 6:
            title = c_el
            title = title.replace('"', "'")
        elif col_idx == 9:
            if c_el and int(c_el) > 5:
                set_goods.add(title)
                goods_cnt += 1
            else:
                pass
    rubrics = {rubric_1, rubric_2}
    print(title)
    try:
        good_obj = get_good_id_by_title(title, connection)
    except InternalError as e:
        print(e)
    else:
        if good_obj and len(good_obj) > 0:
            good_id = good_obj[0]
            counter += 1
            categories = get_good_categories(good_id, connection)
            categories_names = set()
            categories_ids = []

            for category in categories:
                categories_names.add(category[2])
                categories_ids.append(category[6])

            if rubrics != categories_names:
                set_categories_for_good(good_id, rubric_1, rubric_2, categories_ids, connection)


print(counter)