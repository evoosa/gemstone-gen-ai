import os
import pickle

from bs4 import BeautifulSoup

from config import HTMLS_DIR, DATA_DIR, GEMSTONE_DATA_PICKLE_FILE

htmls = os.listdir(HTMLS_DIR)
gemstones_data = []

for html_filename in htmls:
    print(f'parsing {html_filename}')
    gemstone_data = {}
    with open(f'{HTMLS_DIR}/{html_filename}', 'r') as file:
        html_content = file.read()
        soup = BeautifulSoup(html_content, 'html.parser')
        trs = soup.find_all('tr')
        gemstone_data['name'] = html_filename.replace('.html', '')
        for tr in trs:
            contents = tr.contents
            try:
                if (len(contents) == 2) and (contents[0].attrs['class'][0] == 'infobox-label'):
                    label = contents[0].text
                    data = contents[1].text
                    gemstone_data[label] = data
            except:
                pass
        print(gemstone_data)
        gemstones_data.append(gemstone_data)

with open(os.path.join(DATA_DIR, GEMSTONE_DATA_PICKLE_FILE), 'wb') as pickle_f:
    pickle.dump(gemstones_data, pickle_f)
