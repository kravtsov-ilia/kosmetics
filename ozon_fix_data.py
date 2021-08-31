from daily_functions import get_product_title_by_id, get_connection

connection = get_connection('beautyty_db', '3306')
with open('ozon_data', 'r') as f:
    row_numb = 0
    for line in f:
        product_id = line.split(';')[1]
        ozon_id = line.split(';')[2]
        price = int(float(line.split(';')[3]))
        before_price = int(float(line.split(';')[4]))
        if price < 500:
            continue
        title = get_product_title_by_id(product_id, connection)
        if title:
            row_numb += 1
            print('{row_numb};{product_id};{title};{price};{before_price};{ozon_id}'.format(
                row_numb=row_numb,
                product_id=product_id,
                title=title,
                price=price,
                before_price=before_price,
                ozon_id=ozon_id
            ))
