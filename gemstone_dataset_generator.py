import concurrent.futures
import os.path
import pickle

import openai
import pandas as pd

from config import GEMSTONES_FULL_DATA_CSV, GEMSTONES_CLEAN_DATA_CSV, DATA_DIR, GEMSTONE_DATA_PICKLE_FILE, \
    PROMPTS_PICKLE_FILE, PROMPTS_CSV_FILE, DATASET_CSV_FILE


class GemstoneDatasetGenerator:
    # openai gpt query config
    prompt = "Please summarize in a short paragraph the uses of the mineral %s. Your response should explain the various applications and industries that use %s. Please include relevant examples and details to support your explanation. Please note that your response should be flexible enough to allow for various relevant and creative uses of %s. You should focus on providing a comprehensive overview of the mineral's uses, providing insights and information that are not widely known."
    model = 'text-davinci-003'
    max_tokens = 2048

    def __init__(self):
        # openai auth config
        openai.organization = os.getenv("OPENAI_ORG")
        openai.api_key = os.getenv("OPENAI_API_KEY")

        # files config
        self.gems_data_pickle_file = os.path.join(DATA_DIR, GEMSTONE_DATA_PICKLE_FILE)
        self.gems_prompts_pickle_file = os.path.join(DATA_DIR, PROMPTS_PICKLE_FILE)
        self.gems_clean_data_csv_file = os.path.join(DATA_DIR, GEMSTONES_CLEAN_DATA_CSV)
        self.gems_full_data_csv_file = os.path.join(DATA_DIR, GEMSTONES_FULL_DATA_CSV)
        self.gems_prompts_csv_file = os.path.join(DATA_DIR, PROMPTS_CSV_FILE)
        self.gems_dataset_csv_file = os.path.join(DATA_DIR, DATASET_CSV_FILE)
        self.wanted_columns = ["color",
                               "name",
                               "crystal system",
                               "crystal habit",
                               "tenacity",
                               "diaphaneity",
                               "solubility",
                               "mohs scale hardness",
                               "luster"]

        # prompts config
        self.prompt_processes_max_num = 7
        self.prompts = []

        # openai dataset gen config
        self.prompts_suffix = "####"
        self.completion_prefix = "   "
        self.completion_suffix = "$$$$"

    def _generate_gems_full_data_csv(self):
        """
        we don't really need a CSV with all of the data for our training purposes,
        but it could be nice to have all the metadata for the gems just in case
        """
        with open(self.gems_data_pickle_file, 'rb') as gs_pickle_f:
            unpickled_gem_data = pickle.load(gs_pickle_f)

        df = pd.DataFrame(unpickled_gem_data)
        # lowercase the dataframe's contents
        df.columns = df.columns.str.lower()
        df = df.applymap(lambda x: x.lower() if isinstance(x, str) else x)
        df.to_csv(self.gems_full_data_csv_file, index=False)

    def _generate_gems_clean_data_csv(self):
        """ dump only the necessary columns into a CSV with the data needed for training """
        with open(self.gems_full_data_csv_file, 'rb') as output_csv_f:
            df = pd.read_csv(output_csv_f, usecols=self.wanted_columns)
            df.to_csv(self.gems_clean_data_csv_file, index=False)

    @classmethod
    def fetch_prompt_from_openai(cls, gem_data):
        """ ask openai to generate a prompt for a given gem """
        index, gem_name = gem_data[0], gem_data[1]
        prompt_data = {}
        try:
            print(f"\n[!!!] fetching {index}: {gem_name}")
            response = openai.Completion.create(
                engine=cls.model,
                prompt=cls.prompt.replace("%s", gem_name),
                max_tokens=cls.max_tokens,
                n=1,
                stop=None,
                temperature=0.7
            )
            prompt = response.choices[0].text.strip()
            prompt_data['name'] = gem_name
            prompt_data['prompt'] = prompt
            print(f"[VVV] done: {gem_name}")
            return prompt_data
        except Exception as e:
            print(f"\n[XXX] error: {gem_name}\n{e}")

    def _get_prompts_for_all_gems(self):
        """ query openai for prompts to all gems """
        # get gems list
        gems = []
        with open(self.gems_clean_data_csv_file, 'rb') as clean_csv_f:
            df = pd.read_csv(clean_csv_f, usecols=['name'])
            for index, row in df.iterrows():
                gems.append([index, row['name']])
        print(f"\n[!!!] got gems list, {len(gems)} gems")

        # Create a ProcessPoolExecutor with the desired number of processes
        prompts = []
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.prompt_processes_max_num) as executor:
            # Submit the function for each string in the list
            results = [executor.submit(GemstoneDatasetGenerator.fetch_prompt_from_openai, gem_data) for gem_data in
                       gems]
            # Retrieve the results as they become available
            for future in concurrent.futures.as_completed(results):
                result = future.result()
                prompts.append(result)
                print(result)
        self.prompts = prompts

    def _generate_prompts_pickle_file(self):
        """ pickle the prompts, just in case """
        with open(self.gems_prompts_pickle_file, 'wb') as pickle_f:
            pickle.dump(self.prompts, pickle_f)

    def _generate_prompts_csv(self):
        """ create CSV containing all the prompts for all gems """
        with open(self.gems_prompts_pickle_file, 'rb') as pickle_f:
            unpickled_prompts_data = pickle.load(pickle_f)
            unpickled_prompts_data = list(filter(lambda x: x is not None, unpickled_prompts_data))
            df = pd.DataFrame(unpickled_prompts_data)
            df.to_csv(self.gems_prompts_csv_file, index=False)

    def __process_prompts(self, df):
        """ process prompts data to match openai's format for the data preparation tool """
        prompts = []
        for index, row in df.iterrows():
            prompt = row['prompt'] + self.prompts_suffix
            prompts.append({
                'name': row['name'],
                'prompt': prompt
            })
        return prompts

    def __process_completions(self, df):
        """ convert gemstone data into completions that match openai's format for the data preparation tool """
        completions = []
        for index, row in df.iterrows():
            completion = ''
            completion += f'{self.completion_prefix}{row["name"]} is an awesome gemstone. '
            for key, value in row.items():
                if not pd.isnull(value) and (key != 'name'):
                    completion += f'it\'s {key} is {value}. '

            completion += self.completion_suffix
            completions.append({
                'name': row['name'],
                'completion': completion
            })
        return completions

    def _create_dataset(self):
        """ process the completions and prompts to match openai's format, and merge them to a dataset CSV file ready for processing """
        # process prompts
        prompts_csv = pd.read_csv(self.gems_prompts_csv_file)
        prompts_df = pd.DataFrame(self.__process_prompts(prompts_csv))

        # process completions
        gemstone_data_csv = pd.read_csv(self.gems_clean_data_csv_file)
        completions_df = pd.DataFrame(self.__process_completions(gemstone_data_csv))

        # merge prompts+completions into a CSV
        merged_df = pd.merge(prompts_df, completions_df, on='name')
        merged_df.to_csv(self.gems_dataset_csv_file, index=False)
        # remove name column
        df = pd.read_csv(self.gems_dataset_csv_file)
        df = df.drop('name', axis=1)
        df.to_csv(self.gems_dataset_csv_file, index=False)

    def generate_gems_dataset(self):
        """ generate a CSV file with a dataset to train our model on """
        self._generate_gems_full_data_csv()
        print("finished 1")
        self._generate_gems_clean_data_csv()
        print("finished 2")
        self._get_prompts_for_all_gems()
        print("finished 3")
        self._generate_prompts_pickle_file()
        print("finished 4")
        self._generate_prompts_csv()
        print("finished 5")
        self._create_dataset()


if __name__ == '__main__':
    gsdg = GemstoneDatasetGenerator()
    gsdg.generate_gems_dataset()
