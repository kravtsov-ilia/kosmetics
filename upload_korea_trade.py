import argparse
import os

import xlrd

from daily_functions import get_connection, update_post_status, get_all_goods, get_clear_title, find_product_by_title, \
    create_barcode, find_product_by_barcode
from upload import create_product_for_trade

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('--db', help='Use database')
    parser.add_argument('--port', help='Database port')
    parser.add_argument('--img_path', help='Path to image folder')
    parser.add_argument('--date', help='File last update date')
    parser.add_argument('--month', help='Month for find folder')

    args = parser.parse_args()

    database_name = args.db
    database_port = args.port
    date = args.date
    month = args.month
    img_path = args.img_path

    connection = get_connection(database_name, database_port)
    cursor = connection.cursor()


    rb = xlrd.open_workbook('KoreaTrade{}.xls'.format(date))
    sheet = rb.sheet_by_index(0)

    rubrics = set()

    start_row = 4

    set_goods = set()
    goods_cnt = 0

    for i, rownum in enumerate(range(sheet.nrows)):
        if i < start_row:
            continue

        row = sheet.row_values(rownum)
        if not row[0] or row[0] == 'Штрихкод':
            continue

        rubric_1 = None
        rubric_2 = None
        price = None
        scan_code = None
        title = None
        product_id = None

        for col_idx, c_el in enumerate(row):
            if col_idx == 0:
                scan_code = str(c_el)
            if col_idx == 3:
                title = c_el
                product_id = find_product_by_barcode(scan_code, connection)
                if product_id:
                    print('Product already exists: {}'.format(scan_code))
                else:
                    created, created_title = create_product_for_trade(
                        row,
                        'beautyty.org',
                        month,
                        img_path,
                        scan_code,
                        connection
                    )
                    if created:
                        product_data = find_product_by_title(title, connection)
                        product_id = product_data[0][0]
                        print('Product created: {}; ID = {}'.format(title, product_id))
                    else:
                        break

            if col_idx == 5:
                try:
                    stock_count = int(c_el)
                except ValueError:
                    pass
                except TypeError:
                    pass
                else:
                    if stock_count > 10:
                        update_post_status(title, 'instock', connection, product_id)
                        set_goods.add(title)
                        goods_cnt += 1
                        print(title)
                    else:
                        update_post_status(title, 'outofstock', connection, product_id)

        if product_id:
            create_barcode(product_id, scan_code, connection)

    for good in get_all_goods(connection):
        good_id = good[0]
        title = good[1]
        title = title
        if title not in set_goods:
            update_post_status(title, 'outofstock', connection, good_id)

    print("Goods in stock count: {}".format(len(set_goods)))
