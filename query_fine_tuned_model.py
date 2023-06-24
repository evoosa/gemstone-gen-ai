import os
import sys

import openai

prompt = " ".join(sys.argv[1:])

openai.organization = os.getenv("OPENAI_ORG")
openai.api_key = os.getenv("OPENAI_API_KEY")

FINE_TUNED_MODEL = "davinci:ft-startup-2023-06-24-11-23-34"
MAX_TOKENS = 150
PROMPT_SUFFIX = ".####"
STOP_SEQUENCE = "$$$$"

response = openai.Completion.create(
    model=FINE_TUNED_MODEL,
    prompt=prompt + PROMPT_SUFFIX,
    max_tokens=MAX_TOKENS,
    n=1,
    stop=STOP_SEQUENCE,
    temperature=0.7)

output_text = response.choices[0].text.strip()
print(output_text)
