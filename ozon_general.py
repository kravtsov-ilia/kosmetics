import argparse

import xlrd

import brands_map
from daily_functions import get_connection, get_clear_title, find_product_by_title, get_brand, \
    get_product_description_by_id, get_stock_status, get_image_by_id
from functions import find_components

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

    rubrics = set()
    start_row = 16

    include_ids = [
        1311,
        1313,
        1127,
        1225,
        1047,
        1051,
        1221,
        1329,
        277,
        1464,
        2276,
        2294,
        1462,
        3136,
        285,
        295,
        289,
        281,
        3464,
        3408,
        3138,
        3380,
        3466,
        3828,
        3890,
        3808,
        3836,
        3888,
        3898,
        3900,
        3892,
        4024,
        3894,
        4346,
        4208,
        4310,
        4314,
        4344,
        4402,
        4350,
        4348,
        4682,
        4680,
        5300,
        475,
        5280,
        4686,
        4986,
        5322,
        5312,
        5414,
        5310,
        5410,
        5424,
        565,
        567,
        559,
        5422,
        573,
        579,
        581,
        591,
        585,
        603,
        599,
        605,
        593,
        5920,
        663,
        637,
        1936,
        3024,
        1027,
        1510,
        2760,
        3036,
        3820,
        8313,
        4300,
        8043,
        867,
        1938,
        4690,
        1498,
        1542,
        1844,
        1792,
        1514,
        2530,
        2552,
        1940,
        1846,
        2666,
        5712,
        5708,
        3676,
        5296,
        2668,
        5772,
        5950,
        5758,
        4330,
        3908,
        4934,
        4938,
        8947,
        3810,
        4918,
        4914,
        4920,
        5288,
        3936,
        5340,
        5336,
        989,
        997,
        1049,
        985,
        977,
        969,
        953,
        1013,
        965,
        967,
        1672,
        1590,
        1586,
        2440,
        2438,
        4342,
        4340,
        5354,
        4352,
        4908,
        5358,
        3788,
        4312,
        3784,
        4574,
        4564,
        4152,
        4572,
        4584,
        4578,
        4580,
        4582,
        4576,
        4588,
        4608,
        4616,
        4586,
        4610,
        4626,
        4620,
        4622,
        4618,
        4632,
        4650,
        4634,
        4656,
        4660,
        4648,
        5052,
        5056,
        5054,
        5050,
        5048,
        9501,
        3880,
        3884,
        3882,
        5306,
        5484,
        5486,
        5488,
        1245,
        503,
        1522,
        2568,
        1077,
        871,
        937,
        6024,
        5984,
        1383,
        1492,
        1494,
        1129,
        1496,
        1518,
        5714,
        1882,
        337,
        339,
        8037,
        8893,
        6170,
        8089,
        11086,
        11088,
        11092,
        11096,
        11098,
        1379,
        1137,
        2282,
        279,
        275,
        371,
        429,
        283,
        287,
        291,
        8117,
        8137,
        8113,
        8123,
        8119,
        8149,
        917,
        1131,
        1269,
        1075,
        1267,
        1243,
        1271,
        1279,
        1273,
        1277,
        1275,
        1884,
        1748,
        1810,
        1385,
        2566,
        2680,
        5290,
        2744,
        2746,
        2718,
        685,
        8469,
        929,
        1319,
        1265,
        11100,
        1145,
        1241,
        2412,
        2404,
        2402,
        1540,
        1538,
        4916,
        4912,
        6156,
        4924,
        1217,
        2840,
        1141,
        333,
        1223,
        8055,
        361,
        359,
        335,
        1289,
        1293,
        2494,
        1287,
        1291,
        5376,
        2504,
        5378,
        2498,
        5380,
        1173,
        1143,
        1175,
        2698,
        1171,
        561,
        971,
        4904,
        3774,
        5344,
        5382,
        5346,
        8951,
        5384,
        5398,
        8417,
        619,
        1904,
        1315,
        4038,
        4032,
        4046,
        4048,
        4202,
        4206,
        4204,
        1460,
        2350,
        8623,
        1121,
        1135,
        1057,
        1227,
        11094,
        1377,
        1247,
        1375,
        1229,
        1400,
        1534,
        1532,
        1490,
        1488,
        1536,
        2580,
        1570,
        1568,
        1690,
        1566,
        2728,
        2722,
        2708,
        2704,
        2682,
        2970,
        2968,
        3368,
        2740,
        2730,
        353,
        355,
        357,
        349,
        351,
        4338,
        5064,
        5630,
        507,
        445,
        5644,
        5770,
        5636,
        5962,
        5632,
        645,
        615,
        8083,
        8085,
        607,
        813,
        8185,
        8187,
        811,
        8183,
        8411,
        837,
        8875,
        8257,
        855,
        8981,
        891,
        1341,
        1331,
        1339,
        1335,
        1343,
        4404,
        1349,
        1708,
        4406,
        1345,
        4422,
        4410,
        4420,
        4418,
        4412,
        4426,
        4442,
        4438,
        4440,
        4424,
        4452,
        4446,
        4450,
        4448,
        4444,
        4458,
        4462,
        4454,
        4460,
        4456,
        4468,
        4470,
        4466,
        4464,
        4498,
        4502,
        4508,
        4514,
        4520,
        4506,
        4530,
        4528,
        4526,
        4524,
        4532,
        749,
        6044,
        4534,
        751,
        747,
        755,
        761,
        753,
        757,
        759,
        765,
        763,
        767,
        771,
        769,
        773,
        779,
        777,
        775,
        781,
        791,
        783,
        785,
        787,
        789,
        793,
        801,
        799,
        795,
        797,
        8599,
        8601,
        805,
        8605,
        803,
        8607,
        9349,
        9345,
        9347,
        9343,
        9351,
        1410,
        2678,
        271,
        273,
        293,
        427,
        8111,
        425,
        8125,
        8873,
        8141,
        8205,
        8143,
        8203,
        1071,
        1087,
        1085,
        1448,
        1073,
        5160,
        5158,
        8529,
        1674,
        1606,
        1626,
        1634,
        1644,
        5906,
        5902,
        5806,
        347,
        2688,
        6000,
        661,
        2706,
        629,
        1486,
        1373,
        3792,
        647,
        677,
        2984,
        1676,
        3018,
        1466,
        1630,
        5866,
        5908,
        4144,
        4064,
        4058,
        4060,
        4146,
        5036,
        4150,
        5034,
        473,
        3930,
        3932,
        1908,
        471,
        5650,
        9135,
        5100,
        5102,
        9433,
        9435,
        1005,
        1003,
        1007,
        1001,
        8011,
        993,
        991,
        995,
        957,
        8135,
        1011,
        1015,
        961,
        8129,
        1281,
        3846,
        1283,
        1285,
        1355,
        1351,
        1353,
        1357,
        1359,
        1361,
        1363,
        1365,
    ]

    set_goods = set()
    goods_cnt = 0
    row_numb = 0

    with open('ozon_general_file.csv', 'w') as f:
        for i, rownum in enumerate(range(sheet.nrows), start=1):
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
            product_data = None
            description = None
            before_price = None
            product_id = None
            price_30k = None
            raw_title = None

            categ_1 = None
            categ_2 = None

            info = None

            avail_cnt = 0

            for col_idx, c_el in enumerate(row):
                if col_idx == 1:
                    scan_code = int(float(c_el))
                if col_idx == 3:
                    categ_1 = c_el
                if col_idx == 4:
                    categ_2 = c_el
                elif col_idx == 6:
                    raw_title = c_el
                    title = c_el
                    title = title.replace('"', "'")
                    title = get_clear_title(title) or title
                    product_data = find_product_by_title(title, connection)
                    if product_data:
                        product_id = product_data[0][0]
                elif col_idx == 8:
                    info = c_el
                elif col_idx == 9:
                    try:
                        avail_cnt = int(float(c_el))
                    except (TypeError, ValueError):
                        print('Cant get available count for: {}; value: {}'.format(title, c_el))
                elif col_idx == 13:
                    try:
                        price_30k = int(float(c_el))
                    except ValueError:
                        print('Value error price30k: {i}: price: {price}'.format(i=i, price=c_el))
                elif col_idx == 14:
                    try:
                        price = int(float(c_el))
                    except ValueError:
                        print('Value error: {i}: price: {price}'.format(i=i, price=c_el))
                    if not price and price_30k:
                        price = price_30k * 1.65
                        before_price = int(price * 1.4)

            if not product_id or not price:
                continue

            description = get_product_description_by_id(product_id, connection)
            description = description.replace('"', '')

            brand = get_brand(product_id, connection)
            if not brand:
                try:
                    brand = brands_map.brands_map[raw_title.split(' ')[0]]
                except KeyError:
                    print('Brand dont exist: {}'.format(raw_title.split(' ')[0]))

            if not brand:
                continue

            # if product_id in include_ids:
            #     continue

            if categ_1 not in ('Лицо',):
                continue

            if categ_2 not in ('Уход',):
                continue

            if "A'PIEU" not in brand:
                continue

            # if product_id in include_ids:
            #     continue

            if price < 500:
                continue

            if price < 599:
                price = 599
                before_price = int(price * 1.4)

            url = get_image_by_id(product_id, connection)
            if not url:
                continue

            # if avail_cnt > 10:
            #     avail_cnt = 10
            # else:
            avail_cnt = 0

            if price < 640:
                avail_cnt = 0

            components = find_components(scan_code)

            title = title.replace(brand, '')
            row_numb += 1
            f.write('"{row_numb}"; "{product_id}"; "{brand} {title}"; "{price}"; "{before_price}"; '
                    '"{scan_code}"; "{brand}"; "{description}"; "{url}";'
                    '"{avail_cnt}";"{components}"\n'.format(
                row_numb=row_numb,
                product_id=product_id,
                title=title,
                price=int(price),
                before_price=int(price * 1.4),
                scan_code=scan_code,
                brand=brand,
                description=description,
                url=url,
                avail_cnt=avail_cnt,
                components=components
            ))