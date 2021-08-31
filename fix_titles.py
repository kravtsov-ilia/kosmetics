import argparse

import re

from daily_functions import get_connection, get_all_goods, update_post_title

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

for good in get_all_goods(connection):
    post_id = good[0]
    title = good[1]
    if title not in set_goods:
        title = title.replace('"', "'")
        title = re.escape(title)
        update_post_title(post_id, title, connection)