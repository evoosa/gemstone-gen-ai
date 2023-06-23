import os
import pickle

import openai
import pandas as pd

from config import DATA_DIR, GEMSTONES_CLEAN_CSV, PROMPTS_PICKLE_FILE

openai.organization = os.getenv("OPENAI_ORG")
openai.api_key = os.getenv("OPENAI_API_KEY")
PROMPT = "Please summarize in a short paragraph the uses of the mineral %s. Your response should explain the various applications and industries that use %s. Please include relevant examples and details to support your explanation. Please note that your response should be flexible enough to allow for various relevant and creative uses of %s. You should focus on providing a comprehensive overview of the mineral's uses, providing insights and information that are not widely known."

prompts = []
with open(os.path.join(DATA_DIR, GEMSTONES_CLEAN_CSV), 'rb') as output_csv_f:
    df = pd.read_csv(output_csv_f, usecols=['name'])
    for index, row in df.iterrows():
        try:
            gemstone_data = {}
            gemstone_name = row['name']
            print(f"\n[!!!] fetching {index}: {gemstone_name}")
            response = openai.Completion.create(
                engine='text-davinci-003',
                prompt=PROMPT.replace("%s", gemstone_name),
                max_tokens=2048,
                n=1,
                stop=None,
                temperature=0.7
            )
            prompt = response.choices[0].text.strip()
            gemstone_data['name'] = gemstone_name
            gemstone_data['prompt'] = prompt
            prompts.append(gemstone_data)
            print(gemstone_data)
            print(f"[VVV] done: {gemstone_name}")
        except Exception as e:
            print(f"\n[XXX] error: {gemstone_name}\n{e}")

print(prompts)
with open(os.path.join(DATA_DIR, PROMPTS_PICKLE_FILE), 'wb') as pickle_f:
    pickle.dump(prompts, pickle_f)
