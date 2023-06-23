import concurrent.futures
import os
import pickle

import openai
import pandas as pd

from config import DATA_DIR, GEMSTONES_CLEAN_DATA_CSV, PROMPTS_PICKLE_FILE

openai.organization = os.getenv("OPENAI_ORG")
openai.api_key = os.getenv("OPENAI_API_KEY")
PROMPT = "Please summarize in a short paragraph the uses of the mineral %s. Your response should explain the various applications and industries that use %s. Please include relevant examples and details to support your explanation. Please note that your response should be flexible enough to allow for various relevant and creative uses of %s. You should focus on providing a comprehensive overview of the mineral's uses, providing insights and information that are not widely known."
MODEL = 'text-davinci-003'
MAX_TOKENS = 2048


def fetch_prompt(gemstone_data):
    index, gemstone_name = gemstone_data[0], gemstone_data[1]
    prompt_data = {}
    try:
        print(f"\n[!!!] fetching {index}: {gemstone_name}")
        response = openai.Completion.create(
            engine=MODEL,
            prompt=PROMPT.replace("%s", gemstone_name),
            max_tokens=MAX_TOKENS,
            n=1,
            stop=None,
            temperature=0.7
        )
        prompt = response.choices[0].text.strip()
        prompt_data['name'] = gemstone_name
        prompt_data['prompt'] = prompt
        print(prompt_data)
        print(f"[VVV] done: {gemstone_name}")
        return prompt_data
    except Exception as e:
        print(f"\n[XXX] error: {gemstone_name}\n{e}")


# get gemstones list
gemstones = []
with open(os.path.join(DATA_DIR, GEMSTONES_CLEAN_DATA_CSV), 'rb') as output_csv_f:
    df = pd.read_csv(output_csv_f, usecols=['name'])
    for index, row in df.iterrows():
        gemstones.append([index, row['name']])

# gemstones = gemstones[:3]  # FIXME
# print(gemstones)

# Create a ProcessPoolExecutor with the desired number of processes
prompts = []
# num_processes = 3
num_processes = 7
with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes) as executor:
    # Submit the function for each string in the list
    results = [executor.submit(fetch_prompt, gemstone_data) for gemstone_data in gemstones]

    # Retrieve the results as they become available
    for future in concurrent.futures.as_completed(results):
        result = future.result()
        prompts.append(result)

print(prompts)
# pickle all data
print(prompts)
with open(os.path.join(DATA_DIR, PROMPTS_PICKLE_FILE), 'wb') as pickle_f:
    pickle.dump(prompts, pickle_f)
