import pickle

import pandas as pd

from config import OUTPUT_CSV_FILE

with open('gemstones_metadata.pickle', 'rb') as file:
    unpickled_gemstone_data = pickle.load(file)

df = pd.DataFrame(unpickled_gemstone_data)
df.to_csv(OUTPUT_CSV_FILE, index=False)
