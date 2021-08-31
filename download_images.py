import re
import shutil

import mysql.connector
from pip._vendor import requests
from lxml import html
from bs4 import BeautifulSoup

img_post_data = {
    "ID":"64",
    "post_author":"1",
    "post_date":"2019-01-23 13:47:21",
    "post_date_gmt":"2019-01-23 13:47:21",
    "post_content":"",
    "post_title":"Dry_Slub_Long_Sleeve_Navy_1024x1024",
    "post_excerpt":"",
    "post_status":"inherit",
    "comment_status":"open",
    "ping_status":"closed",
    "post_password":"",
    "post_name":"dry_slub_long_sleeve_navy_1024x1024",
    "to_ping":"",
    "pinged":"",
    "post_modified":"2019-01-23 13:47:21",
    "post_modified_gmt":"2019-01-23 13:47:21",
    "post_content_filtered":"",
    "post_parent":"63",
    "guid":"https:\/\/beautyty.org\/wp-content\/uploads\/2019\/01\/Dry_Slub_Long_Sleeve_Navy_1024x1024.jpg",
    "menu_order":"0",
    "post_type":"attachment",
    "post_mime_type":"image\/jpeg",
    "comment_count":"0"
}

changed_fields = ("ID", "post_title", "post_name", "guid")

guid_template = "https:\/\/beautyty.org\/wp-content\/uploads\/2019\/01\/{file_name}"

connection = mysql.connector.connect(
    host='localhost',
    database='bloggers_db',
    user='w3data',
    password='qwerty!@#',
    port='8889'
)

cursor = connection.cursor()

cursor.execute("select * from wp_posts ORDER by ID DESC limit 1")

last_post = cursor.fetchone()
last_post_id = last_post[0]

post_columns = ['ID', 'post_author', 'post_date', 'post_date_gmt', 'post_content', 'post_title', 'post_excerpt', 'post_status', 'comment_status', 'ping_status', 'post_password', 'post_name', 'to_ping', 'pinged', 'post_modified', 'post_modified_gmt', 'post_content_filtered', 'post_parent', 'guid', 'menu_order', 'post_type', 'post_mime_type', 'comment_count']
cursor.execute("select * from wp_posts WHERE ID > 70")

for row in cursor.fetchall():
    title = row[5]

    google_url = 'https://www.google.com/search?q={title}&source=lnms&tbm=isch&sa=X&ved=0ahUKEwjw64PugorgAhXI_SwKHbcMDiYQ_AUIDigB&biw=1440&bih=690'
    yandex_url = 'https://yandex.ru/images/search?text={title}'

    response = requests.get(url=yandex_url.format(title=title))

    tree = html.fromstring(response.text)

    tags = tree.xpath('//a[@class="serp-item__link"]')

    film_list_lxml = tree.xpath('//img[@alt = "Картинки по запросу {0}"]'.format(title))[0]

    img_link = film_list_lxml.attrib['src']

    response = requests.get(url=img_link)

    with open('/Users/ikravtsov/Downloads/{post_id}.jpg'.format(post_id=row[0]), 'wb') as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)

    a = 1
