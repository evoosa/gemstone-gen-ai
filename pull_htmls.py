import csv
import os.path

import requests

from config import HTMLS_DIR, GEMSTONE_URLS_CSV_FILE, DATA_DIR

with open(os.path.join(DATA_DIR, GEMSTONE_URLS_CSV_FILE), 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        website_url = row[0]
        gemstone_name = row[1]
        print(f"\n[!!!] fetching: {gemstone_name}, {website_url}")
        try:
            response = requests.get(website_url)
            if response.status_code == requests.codes.ok:
                with open(f'{HTMLS_DIR}/{gemstone_name}.html', "w") as html_f:
                    html_f.write(response.text)
                print(f"[VVV] success: {gemstone_name}")
            else:
                print(f'[XXX] failed to make the request: {response.status_code}')
        except Exception as e:
            print(f'failed to get: {website_url}\n{e}')
