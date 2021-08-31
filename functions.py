import xlrd

from constants import img_post_data, img_guid_template, img_meta_1, img_meta_1_value_template, img_meta_2, \
    img_meta_2_value_template

post_columns = ['post_author', 'post_date', 'post_date_gmt', 'post_content', 'post_title', 'post_excerpt', 'post_status', 'comment_status', 'ping_status', 'post_password', 'post_name', 'to_ping', 'pinged', 'post_modified', 'post_modified_gmt', 'post_content_filtered', 'post_parent', 'guid', 'menu_order', 'post_type', 'post_mime_type', 'comment_count']


def create_post(post_obj, connection):
    values_list = []

    for key in post_columns:
        if key in ('post_content', ):
            val = post_obj[key].replace('"', "'")
            if val.startswith('Пр-ль'):
                val = 'Производитель' + val[5:]
        else:
            val = post_obj[key]
        values_list.append('"' + str(val) + '"')

    a = ','.join(post_columns)
    b = ','.join(values_list)
    request = "INSERT INTO wp_posts ({cols}) VALUES ({vals})".format(cols=a, vals=b)

    cursor = connection.cursor()
    cursor.execute(request)
    connection.commit()

    cursor.execute("select * from wp_posts ORDER by ID DESC limit 1")

    last_post = cursor.fetchall()[0]
    last_post_id = last_post[0]
    post_obj['ID'] = last_post_id


def create_postmeta(meta_obj, connection):

    meta_columns = ["post_id", "meta_key", "meta_value"]
    meta_values = []

    for key in meta_columns:
        meta_values.append("'" + str(meta_obj[key]) + "'")

    request = "INSERT INTO wp_postmeta ({cols}) VALUES ({vals})".format(cols=','.join(meta_columns), vals=','.join(meta_values))

    cursor = connection.cursor()
    cursor.execute(request)
    connection.commit()


def create_terms(term_obj, post_obj, is_need_create_term, connection):
    term_columns = ["name", "slug", "term_group"]
    term_values = []

    for key in term_columns:
        term_values.append('"' + str(term_obj[key]) + '"')

    cursor = connection.cursor(buffered=True)
    if is_need_create_term or term_obj['term_id'] is None:
        request = "INSERT INTO wp_terms ({cols}) VALUES ({vals})".format(
            cols=','.join(term_columns),
            vals=','.join(term_values)
        )

        cursor.execute(request)
        connection.commit()

        cursor.execute("""
        select * from wp_terms WHERE name="{term_name}" ORDER by term_id DESC limit 1
        """.format(term_name=term_obj['name']))
        last_term_data = cursor.fetchall()[0]
        last_term_id = last_term_data[0]
        term_obj['term_id'] = last_term_id

        request_for_taxonomy = "INSERT INTO wp_term_taxonomy (term_id, taxonomy, description, parent, count) " \
        "values ({}, 'product_cat', '', 0, 0);".format(last_term_id)

        cursor.execute(request_for_taxonomy)
        connection.commit()

    request = """
    select term_taxonomy_id from wp_term_taxonomy where term_id = {term_id} ORDER by term_taxonomy_id DESC limit 1
    """.format(term_id=term_obj['term_id'])
    cursor.execute(request)

    taxonomy = cursor.fetchall()[0]
    taxonomy_id = taxonomy[0]

    try:
        request = "INSERT INTO wp_term_relationships (object_id, term_taxonomy_id, term_order) VALUES (" \
              "{post_id},{taxonomy_id},0)".format(post_id=post_obj["ID"], taxonomy_id=taxonomy_id)
        cursor.execute(request)
        connection.commit()
    except Exception:
        pass


def create_images(img_obj, meta_1, meta_2, connection):
    img_columns = post_columns
    img_values = []

    for key in img_columns:
        img_values.append("'" + str(img_obj[key]) + "'")

    request = "INSERT INTO wp_posts ({cols}) VALUES ({vals})".format(
        cols=','.join(img_columns), vals=','.join(img_values)
    )

    cursor = connection.cursor()
    cursor.execute(request)
    connection.commit()

    meta_columns = ["post_id", "meta_key", "meta_value"]
    for meta in [meta_1, meta_2]:
        meta_values = []

        for key in meta_columns:
            meta_values.append("'" + str(meta[key]) + "'")

        request = "INSERT INTO wp_postmeta ({cols}) VALUES ({vals})".format(cols=','.join(meta_columns),
                                                                            vals=','.join(meta_values))

        cursor = connection.cursor()
        cursor.execute(request)
        connection.commit()


def prepare_images(new_post_record_data, last_post_id, image_name, domain, month, connection):
    img_obj = img_post_data
    img_obj["ID"] = last_post_id + 1
    img_obj["post_title"] = new_post_record_data["post_name"]
    img_obj["post_name"] = new_post_record_data["post_name"]
    img_obj["post_parent"] = new_post_record_data["ID"]
    img_obj["guid"] = img_guid_template.format(
        slug=image_name,
        domain=domain,
        month=month
    )

    meta_1 = img_meta_1
    meta_1["post_id"] = img_obj["ID"]
    meta_1["meta_value"] = img_meta_1_value_template.format(
        slug=image_name,
        month=month
    )

    meta_2 = img_meta_2
    meta_2["post_id"] = img_obj["ID"]
    meta_2["meta_value"] = img_meta_2_value_template.format(
        slug=image_name,
        month=month
    )

    create_images(img_obj, meta_1, meta_2, connection)

    return img_obj


def find_components(scan_code):
    start_row = 12
    rb = xlrd.open_workbook('Polnyiy assortiment KEAUTY s RRTS 2020.xls')
    sheet = rb.sheet_by_index(0)
    for i, rownum in enumerate(range(sheet.nrows)):
        if i < start_row:
            continue

        row = sheet.row_values(rownum)
        if not row[1] or row[1] == 'Штрихкод':
            continue

        if row[1] == scan_code:
            return row[10]

    return None
