import mysql.connector
import re

from transliterate import slugify

import brands_map
from functions import create_terms


def get_connection(database_name, database_port):
    return mysql.connector.connect(
        host='localhost',
        database=database_name,
        user='w3data',
        password='0',
        port=database_port,
        auth_plugin='mysql_native_password'
    )


def find_product_in_general_file(products, product_title):
    if product_title in products:
        print('Product have data in general file')
        return True
    else:
        return False


def update_post_status(title, status, connection, product_id):
    request = """
    UPDATE wp_postmeta set meta_value="{status}" WHERE post_id={product_id} AND meta_key='_stock_status'
    """.format(product_id=product_id, status=status)
    cursor = connection.cursor()
    cursor.execute(request)
    connection.commit()
    if cursor.rowcount == 0:
        print('Cant find for update: {}'.format(title))


def get_stock_status(product_id, connection):
    request = """
    SELECT meta_value FROM wp_postmeta WHERE post_id={product_id} AND meta_key='_stock_status'
    """.format(product_id=product_id)
    cursor = connection.cursor()
    cursor.execute(request)
    res = cursor.fetchall()
    return res[0] if len(res) > 0 else None


def get_all_goods(connection):
    request = "SELECT id, post_title FROM wp_posts WHERE post_type='product'"
    cursor = connection.cursor()
    cursor.execute(request)
    return cursor.fetchall()


def get_good_id_by_title(title, connection):
    request = """
    SELECT ID FROM wp_posts WHERE post_type='product' AND post_title="{title}"
    """.format(title=title)
    cursor = connection.cursor()
    cursor.execute(request)
    res = cursor.fetchall()
    return res[0] if len(res) > 0 else None


def get_good_categories(good_id, connection):
    request = """
    SELECT 
        T.term_id, 
        R.object_id,
        T.name,
        T.slug, 
        X.term_taxonomy_id, 
        X.taxonomy,
        R.term_taxonomy_id
    FROM wp_term_taxonomy X 
    INNER join wp_terms T ON T.term_id = X.term_id 
    INNER join wp_term_relationships R on R.term_taxonomy_id = X.term_taxonomy_id  
    WHERE X.taxonomy = 'product_cat' AND R.object_id={good_id}
    ORDER BY R.term_taxonomy_id
    """.format(good_id=good_id)
    cursor = connection.cursor()
    cursor.execute(request)
    return cursor.fetchall()


def update_post_title(good_id, title, connection):
    request = """
        UPDATE wp_posts set post_title="{title} WHERE ID={good_id}"
        """.format(good_id=good_id, title=title)
    cursor = connection.cursor()
    cursor.execute(request)
    connection.commit()


def set_categories_for_good(good_id, rubric_1, rubric_2, old_categories_ids_list, connection):
    if old_categories_ids_list:
        remove_old_catigories = """
            DELETE FROM wp_term_relationships 
            WHERE object_id = {good_id} 
            AND term_taxonomy_id IN ({ids}) 
            """.format(good_id=good_id, ids=','.join(str(x) for x in old_categories_ids_list))

        cursor = connection.cursor()
        cursor.execute(remove_old_catigories)
        connection.commit()

    cat_data_1 = find_category_id(rubric_1, connection)
    cat_data_2 = find_category_id(rubric_2, connection)

    cat_id_1 = None
    cat_id_2 = None

    if cat_data_1 and len(cat_data_1) > 0:
        cat_id_1 = cat_data_1[0]
    else:
        print('Category `{}` not found'.format(rubric_1))

    if cat_data_2 and len(cat_data_2) > 0:
        cat_id_2 = cat_data_2[0]
    else:
        print('Category `{}` not found'.format(rubric_2))

    if not cat_id_1 or not cat_id_2:
        print('Something go wrong: cat_id_1 = {}; cat_id_2 = {}'.format(cat_id_1, cat_id_2))

    cursor = connection.cursor()
    for cat_id in [cat_id_1, cat_id_2]:
        try:
            request = """
            INSERT INTO 
            wp_term_relationships (object_id, term_taxonomy_id, term_order) 
            VALUES ({post_id},{taxonomy_id},0) """.format(post_id=good_id, taxonomy_id=cat_id)
            cursor.execute(request)
            connection.commit()
        except Exception as e:
            print(e)


def find_category_id(category, connection):
    request = """
    SELECT 
        X.term_taxonomy_id 
    FROM wp_term_taxonomy X 
    INNER join wp_terms T ON T.term_id = X.term_id 
    WHERE T.name = "{category}"
    """.format(category=category)

    cursor = connection.cursor()
    cursor.execute(request)
    return cursor.fetchall()[0]


def find_term_id(slug, connection):
    request = """
    SELECT 
        term_id 
    FROM wp_terms  
    WHERE slug = "{slug}"
    """.format(slug=slug)

    cursor = connection.cursor(buffered=True)
    try:
        cursor.execute(request)
        res = cursor.fetchall()
        return res[0] if len(res) > 0 else None
    except Exception as e:
        print(e)
        print(request)


def has_cyrillic(text):
    return bool(re.search('[а-яА-Я]', text))


def get_clear_title(title):
    title_without_brand = None
    words = title.split(' ')

    if words[0] in brands_map.brands_map:
        del words[0]

    for i, word in enumerate(words):
        if has_cyrillic(word):
            title_without_brand = ' '.join([x for x in words[i:]])
            if len(title_without_brand.split(' ')) < 5:
                print('Слишком мало русских слов: {0}'.format(title))
                title_without_brand = None
            break
    return title_without_brand


def remove_brand_from_title(title, connection):
    title_without_brand = get_clear_title(title) or title

    request = """
        UPDATE wp_posts set post_title="{title_without_brand}" WHERE post_title="{title}"
        """.format(title_without_brand=title_without_brand, title=title)

    cursor = connection.cursor()
    cursor.execute(request)
    connection.commit()


def set_brand_category(good_id, category, connection):
    term_slug = slugify(category) or ''.join([x for x in category if x.isalnum()])

    brand_category_data = find_term_id(term_slug, connection)
    is_need_create = False
    if not brand_category_data:
        is_need_create = True
        brand_category_id = None
    else:
        brand_category_id = brand_category_data[0]

    post_obj = {
        'ID': good_id
    }
    term_obj = {
        'term_id': brand_category_id,
        'name': category,
        'slug': term_slug,
        'term_group': 0
    }

    create_terms(term_obj, post_obj, is_need_create, connection)


def find_product_by_title(title, connection):
    request = """
        SELECT id FROM wp_posts WHERE post_title like "%{title}" LIMIT 1
        """.format(title=title)
    cursor = connection.cursor()
    cursor.execute(request)
    return cursor.fetchall()


def find_product_by_barcode(barcode, connection):
    request = """
            SELECT post_id FROM wp_postmeta WHERE meta_key = 'barcode' AND meta_value = '{barcode}' LIMIT 1
            """.format(barcode=barcode)
    cursor = connection.cursor()
    cursor.execute(request)
    post_id = cursor.fetchall()
    if post_id:
        return post_id[0][0]
    else:
        return None


def get_brand(good_id, connection):
    brands = [value for key, value in brands_map.brands_map.items()]
    request = """
    SELECT
      T.name
    FROM wp_term_relationships R
    inner join wp_term_taxonomy X ON R.term_taxonomy_id = X.term_taxonomy_id
    inner join wp_terms T ON  T.term_id = X.term_id
    WHERE R.object_id = {good_id}
    """.format(good_id=good_id)
    cursor = connection.cursor()
    cursor.execute(request)
    for term in cursor.fetchall():
        category_name = term[0]
        if category_name in brands:
            return category_name
    return None


def get_category(good_id, connection):
    brands = [value for key, value in brands_map.brands_map.items()]
    request = """
    SELECT
      T.name
    FROM wp_term_relationships R
    inner join wp_term_taxonomy X ON R.term_taxonomy_id = X.term_taxonomy_id
    inner join wp_terms T ON  T.term_id = X.term_id
    WHERE R.object_id = {good_id}
    """.format(good_id=good_id)
    cursor = connection.cursor()
    cursor.execute(request)
    for term in cursor.fetchall():
        category_name = term[0]
        if category_name not in brands:
            return category_name
    return None


def get_price_by_id(product_id, connection):
    request = 'SELECT meta_value FROM wp_postmeta WHERE meta_key = "_price" and post_id = {post_id}'.format(post_id=product_id)
    cursor = connection.cursor()
    cursor.execute(request)
    return cursor.fetchall()[0][0]


def get_product_title_by_id(product_id, connection):
    request = """
        SELECT post_title FROM wp_posts WHERE post_type='product' AND ID="{product_id}"
        """.format(product_id=product_id)
    cursor = connection.cursor()
    cursor.execute(request)
    res = cursor.fetchall()
    return res[0][0] if len(res) > 0 else None

def get_product_description_by_id(product_id, connection):
    request = """
        SELECT post_content FROM wp_posts WHERE post_type='product' AND ID="{product_id}"
        """.format(product_id=product_id)
    cursor = connection.cursor()
    cursor.execute(request)
    res = cursor.fetchall()
    return res[0][0] if len(res) > 0 else None


def get_image_by_id(product_id, connection):
    request = """
    SELECT P2.guid
    FROM wp_postmeta M INNER JOIN wp_posts P ON M.post_id = P.ID
    INNER JOIN wp_posts P2 ON P2.ID = M.meta_value
    WHERE  M.meta_key = '_thumbnail_id' AND P.ID="{product_id}"
    """.format(product_id=product_id)
    cursor = connection.cursor()
    cursor.execute(request)
    res = cursor.fetchall()
    return res[0][0] if len(res) > 0 else None


def get_product_url(product_id, connection):
    request = """
        SELECT post_name
        FROM wp_posts
        WHERE  post_type = 'product' AND ID="{product_id}"
    """.format(product_id=product_id)
    cursor = connection.cursor()
    cursor.execute(request)
    res = cursor.fetchall()
    slug = res[0][0] if len(res) > 0 else None
    if slug:
        return 'https://beautyty.org/product/{}/'.format(slug)
    else:
        return None


def create_barcode(product_id, barcode, connection):
    if get_barcode(product_id, connection) is not None:
        return None

    cursor = connection.cursor()
    request = """
        INSERT INTO 
        wp_postmeta (post_id, meta_key, meta_value) 
        VALUES ({post_id}, 'barcode', '{barcode}') """.format(post_id=product_id, barcode=barcode)
    cursor.execute(request)
    connection.commit()


def get_barcode(product_id, connection):
    request = """
            SELECT meta_value
            FROM wp_postmeta
            WHERE  meta_key = 'barcode' AND post_id="{product_id}"
        """.format(product_id=product_id)
    cursor = connection.cursor()
    cursor.execute(request)
    res = cursor.fetchall()
    return res[0][0] if len(res) > 0 else None


def get_categories(connection):
    request = """select term_id, name from wp_terms"""
    cursor = connection.cursor()
    cursor.execute(request)
    terms = cursor.fetchall()
    categories_list = []
    for term in terms:
        categories_list.append((term[0], term[1]))

    return categories_list
