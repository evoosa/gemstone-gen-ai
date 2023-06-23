import os
import pickle

import pandas as pd

from config import DATA_DIR, PROMPTS_PICKLE_FILE, PROMPTS_CSV_FILE, GEMSTONES_CLEAN_DATA_CSV, DATASET_CSV_FILE


def output_prompts_to_csv():
    with open(os.path.join(DATA_DIR, PROMPTS_PICKLE_FILE), 'rb') as pickle_f:
        unpickled_prompts_data = pickle.load(pickle_f)
        unpickled_prompts_data = list(filter(lambda x: x is not None, unpickled_prompts_data))
        df = pd.DataFrame(unpickled_prompts_data)
        df.to_csv(os.path.join(DATA_DIR, PROMPTS_CSV_FILE), index=False)


def create_dataset():
    prompts_df = pd.read_csv(os.path.join(DATA_DIR, PROMPTS_CSV_FILE))

    gemstone_data_csv = pd.read_csv(os.path.join(DATA_DIR, GEMSTONES_CLEAN_DATA_CSV))

    completions = create_completions(gemstone_data_csv)
    completions_df = pd.DataFrame(completions)

    merged_df = pd.merge(prompts_df, completions_df, on='name')
    merged_df.to_csv(os.path.join(DATA_DIR, DATASET_CSV_FILE), index=False)


def create_completions(df):
    completions = []
    for index, row in df.iterrows():
        completion = ''
        completion += f'{row["name"]} is an awesome gemstone. '
        for key, value in row.items():
            if not pd.isnull(value) and (key != 'name'):
                completion += f'it\'s {key} is {value}. '
        completions.append({
            'name': row['name'],
            'completion': completion
        })
    return completions


if __name__ == '__main__':
    create_dataset()
