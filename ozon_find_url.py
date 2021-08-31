import csv


def find_url_by_title(origin_title):
    with open('export-all-urls-579607.CSV') as f:
        spamreader = csv.reader(f, delimiter=',')
        for row in spamreader:
            csv_title = row[0]
            url = row[1]
            if csv_title == origin_title:
                return url
    return None