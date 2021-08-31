import argparse
import os

import mysql.connector
import xlrd
from transliterate import slugify

from constants import guid_template, post_data, meta_data_list
from daily_functions import get_clear_title
from functions import create_post, create_postmeta, create_terms, prepare_images

if __name__ == '__main__':

    changed_fields = ('_thumbnail_id', '_regular_price', '_price')

    parser = argparse.ArgumentParser()

    parser.add_argument('--db', help='Use database')
    parser.add_argument('--port', help='Database port')
    parser.add_argument('--img_path', help='Path to goods images')
    parser.add_argument('--domain', help='New site domain')
    parser.add_argument('--month', help='Current month number: 01 - January, 02 - February etc.')

    args = parser.parse_args()

    database_name = args.db
    database_port = args.port
    images_directory = args.img_path
    domain = args.domain + '\/'
    month = args.month

    connection = mysql.connector.connect(
        host='localhost',
        database=database_name,
        user='w3data',
        password='0',
        port=database_port
    )

    cursor = connection.cursor()

    rb = xlrd.open_workbook('keauty_prices.xlsx')
    sheet = rb.sheet_by_index(0)

    rubrics = set()

    for i, rownum in enumerate(range(sheet.nrows)):
        row = sheet.row_values(rownum)

        if not row[1] or row[1] == 'Штрихкод':
            continue



    USES_TABLES = {
        'post': 'wp_posts',
        'post_meta': 'wp_postmeta',
        'terms': 'wp_terms',
        'term_to_post': 'wp_term_relationships',
        'taxonomy': 'wp_term_taxonomy'
    }


def create_product(xl_row, domain, list_images_names, month, barcode, connection):
    new_post_record_data = post_data
    new_post_record_data["guid"] = guid_template.format(
        domain=domain,
        new_post_id=new_post_record_data["ID"]
    )
    new_post_record_data["post_status"] = "draft"

    rubric_1 = None
    rubric_2 = None
    price = None
    scan_code = None
    price_30k = None
    title = None

    for col_idx, c_el in enumerate(xl_row):
        if col_idx == 1:
            scan_code = str(int(c_el))
        if col_idx == 3:
            rubric_1 = c_el
        if col_idx == 4:
            rubric_2 = c_el
        if col_idx == 6:
            title = c_el
            title = title.replace('"', "'")
            title = get_clear_title(title) or title
            new_post_record_data["post_title"] = title
            new_post_record_data["post_name"] = slugify(title)
        if col_idx == 13:
            price_30k = c_el
        if col_idx == 14:
            price = c_el
        if col_idx == 16:
            new_post_record_data["post_content"] = c_el

    if not price:
        try:
            price = int(price_30k * 1.65) + 1
        except Exception:
            print('No price found for: {}; barcode: {}'.format(new_post_record_data["post_title"], barcode))
            return None, None

    images_names = [x for x in list_images_names if x.startswith(scan_code)]

    if not images_names:
        print('No images for: {}; barcode: {}'.format(new_post_record_data["post_title"], barcode))
        return None, None

    create_post(new_post_record_data, connection)

    if scan_code not in images_names:
        scan_code = images_names[0]

    img_obj = prepare_images(
        new_post_record_data, new_post_record_data["ID"], scan_code, domain, month, connection
    )

    main_image_id = img_obj["ID"]

    for i, meta in enumerate(meta_data_list, start=1):
        new_post_meta_data = meta
        new_post_meta_data['post_id'] = new_post_record_data["ID"]

        if new_post_meta_data['meta_key'] == '_thumbnail_id':
            new_post_meta_data['meta_value'] = main_image_id

        elif new_post_meta_data['meta_key'] == '_regular_price':
            new_post_meta_data['meta_value'] = str(price)

        elif new_post_meta_data['meta_key'] == '_price':
            new_post_meta_data['meta_value'] = str(price)

        create_postmeta(new_post_meta_data, connection)

    for k, rubric in enumerate([rubric_1, rubric_2], start=1):
        if not rubric:
            continue

        request_string = "select * from wp_terms where name = '{name}' ORDER by term_id DESC limit 1".format(
            name=rubric
        )

        cursor = connection.cursor()
        cursor.execute(request_string)
        term_data = cursor.fetchall()
        try:
            term_id = term_data[0][0]
        except TypeError:
            term_id = None

        term_obj = {
            "term_id": term_id,
            "name": rubric,
            "slug": slugify(rubric),
            "term_group": 0
        }

        create_terms(term_obj, new_post_record_data, False if term_id else True, connection)
    return True, title


def create_product_for_trade(xl_row, domain, month, img_path, barcode, connection):
    new_post_record_data = post_data
    new_post_record_data["guid"] = guid_template.format(
        domain=domain,
        new_post_id=new_post_record_data["ID"]
    )
    new_post_record_data["post_status"] = "publish"

    price = None
    scan_code = None
    title = None

    for col_idx, c_el in enumerate(xl_row):
        if col_idx == 0:
            scan_code = str(int(c_el))
        if col_idx == 3:
            title = c_el
            new_post_record_data["post_title"] = title
            new_post_record_data["post_name"] = slugify(title)
        if col_idx == 11:
            price = int(float(c_el))
        if col_idx == 13:
            new_post_record_data["post_content"] = c_el

    if not price:
        print('No price found for: {}; barcode: {}'.format(new_post_record_data["post_title"], barcode))
        return None, None
    else:
        price = 1.1*price

    image_file = '{}/{}.jpg'.format(img_path, scan_code)

    if not os.path.isfile(image_file):
        print('Korea Torg: No image found {}'.format(scan_code))
        return None, None

    create_post(new_post_record_data, connection)

    img_obj = prepare_images(
        new_post_record_data, new_post_record_data["ID"], scan_code, domain, month, connection
    )

    main_image_id = img_obj["ID"]

    for i, meta in enumerate(meta_data_list, start=1):
        new_post_meta_data = meta
        new_post_meta_data['post_id'] = new_post_record_data["ID"]

        if new_post_meta_data['meta_key'] == '_thumbnail_id':
            new_post_meta_data['meta_value'] = main_image_id

        elif new_post_meta_data['meta_key'] == '_regular_price':
            new_post_meta_data['meta_value'] = str(price)

        elif new_post_meta_data['meta_key'] == '_price':
            new_post_meta_data['meta_value'] = str(price)

        create_postmeta(new_post_meta_data, connection)

    return True, title
