import os

import pandas as pd

from config import DATA_DIR, PROMPTS_CSV_FILE, GEMSTONES_CLEAN_DATA_CSV, DATASET_CSV_FILE

PROMPTS_SUFFIX = "####"
COMPLETION_PREFIX = "   "
COMPLETION_SUFFIX = "$$$$"


def create_dataset():
    # process prompts
    prompts_csv = pd.read_csv(os.path.join(DATA_DIR, PROMPTS_CSV_FILE))
    prompts = process_prompts(prompts_csv)
    prompts_df = pd.DataFrame(prompts)

    # process completions
    gemstone_data_csv = pd.read_csv(os.path.join(DATA_DIR, GEMSTONES_CLEAN_DATA_CSV))
    completions = process_completions(gemstone_data_csv)
    completions_df = pd.DataFrame(completions)

    # merge prompts+completions into a CSV
    merged_df = pd.merge(prompts_df, completions_df, on='name')
    merged_df.to_csv(os.path.join(DATA_DIR, DATASET_CSV_FILE), index=False)
    # remove name column
    df = pd.read_csv(os.path.join(DATA_DIR, DATASET_CSV_FILE))
    df = df.drop('name', axis=1)
    df.to_csv(os.path.join(DATA_DIR, DATASET_CSV_FILE), index=False)


def process_prompts(df):
    """ process prompts data to match openai's format for the data preparation tool """
    prompts = []
    for index, row in df.iterrows():
        prompt = row['prompt'] + PROMPTS_SUFFIX
        prompts.append({
            'name': row['name'],
            'prompt': prompt
        })
    return prompts


def process_completions(df):
    """ convert gemstone data into completions that match openai's format for the data preparation tool """
    completions = []
    for index, row in df.iterrows():
        completion = ''
        completion += f'{COMPLETION_PREFIX}{row["name"]} is an awesome gemstone. '
        for key, value in row.items():
            if not pd.isnull(value) and (key != 'name'):
                completion += f'it\'s {key} is {value}. '

        completion += COMPLETION_SUFFIX
        completions.append({
            'name': row['name'],
            'completion': completion
        })
    return completions


if __name__ == '__main__':
    create_dataset()
