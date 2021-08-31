import argparse

import re

from daily_functions import get_all_goods, get_connection, remove_brand_from_title

parser = argparse.ArgumentParser()

parser.add_argument('--db', help='Use database')
parser.add_argument('--port', help='Database port')

args = parser.parse_args()

database_name = args.db
database_port = args.port


connection = get_connection(database_name, database_port)
cursor = connection.cursor()

for good in get_all_goods(connection):
    remove_brand_from_title(good[1], connection)