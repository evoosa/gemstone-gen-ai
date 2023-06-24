import csv
import os.path
import pickle

import requests
from bs4 import BeautifulSoup

from config import HTMLS_DIR, GEMSTONE_URLS_CSV_FILE, DATA_DIR, GEMSTONE_DATA_PICKLE_FILE


class GemstoneCrawler:
    def __init__(self):
        self.htmls_dir = HTMLS_DIR
        self.gemstone_htmls_csv = os.path.join(DATA_DIR, GEMSTONE_URLS_CSV_FILE)
        self.gemstones_data_pickle_file = os.path.join(DATA_DIR, GEMSTONE_DATA_PICKLE_FILE)
        self.gemstones_data = []

    def _pull_gemstone_htmls(self):
        """ download HTMLs containing gemstones data from wikipedia """
        with open(self.gemstone_htmls_csv, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                website_url = row[0]
                gemstone_name = row[1]
                print(f"\n[!!!] fetching: {gemstone_name}, {website_url}")
                try:
                    response = requests.get(website_url)
                    if response.status_code == requests.codes.ok:
                        with open(f'{self.htmls_dir}/{gemstone_name}.html', "w") as html_f:
                            html_f.write(response.text)
                        print(f"[VVV] success: {gemstone_name}")
                    else:
                        print(f'[XXX] failed to make the request: {response.status_code}')
                except Exception as e:
                    print(f'failed to get: {website_url}\n{e}')

    def _parse_htmls(self):
        """ get the gemstones data from the HTML file """
        htmls = os.listdir(self.htmls_dir)
        gemstones_data = []

        for html in htmls:
            print(f'parsing {html}')
            gemstone_data = {}
            with open(f'{self.htmls_dir}/{html}', 'r') as file:
                html_content = file.read()
                soup = BeautifulSoup(html_content, 'html.parser')
                trs = soup.find_all('tr')
                gemstone_data['name'] = html.replace('.html', '')
                for tr in trs:
                    contents = tr.contents
                    try:
                        if (len(contents) == 2) and (contents[0].attrs['class'][0] == 'infobox-label'):
                            label = contents[0].text
                            data = contents[1].text
                            gemstone_data[label] = data
                    except:
                        pass
                gemstones_data.append(gemstone_data)
        self.gemstones_data = gemstones_data

    def _pickle_gemstones_data(self):
        """ dump the gemstone data into a pickle file """
        with open(self.gemstones_data_pickle_file, 'wb') as pickle_f:
            pickle.dump(self.gemstones_data, pickle_f)
        print(f'[VVV] pickled gemstone data into: {self.gemstones_data_pickle_file}')

    def pickle_gemstones_data(self):
        self._pull_gemstone_htmls()
        self._parse_htmls()
        self._pickle_gemstones_data()


if __name__ == '__main__':
    gc = GemstoneCrawler()
    gc.pickle_gemstones_data()
