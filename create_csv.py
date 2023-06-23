import os.path
import pickle

import pandas as pd

from config import OUTPUT_CSV_FILE, DATASET_CSV_FILE, DATA_DIR, GEMSTONE_METADATA_PICKLE_FILE


def get_full_gemstones_csv():
    with open(os.path.join(DATA_DIR, GEMSTONE_METADATA_PICKLE_FILE), 'rb') as gs_md_pickle_f:
        unpickled_gemstone_data = pickle.load(gs_md_pickle_f)

    df = pd.DataFrame(unpickled_gemstone_data)
    df.to_csv(os.path.join(DATA_DIR, OUTPUT_CSV_FILE), index=False)


def create_dataset():
    columns = ["color",
               "name",
               "crystal system",
               "crystal habit",
               "tenacity",
               "diaphaneity",
               "solubility",
               "mohs scale hardness",
               "luster"]
    with open(os.path.join(DATA_DIR, OUTPUT_CSV_FILE), 'rb') as output_csv_f:
        df = pd.read_csv(output_csv_f, usecols=columns)
        df.to_csv(os.path.join(DATA_DIR, DATASET_CSV_FILE), index=False)


if __name__ == '__main__':
    create_dataset()
