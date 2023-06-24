import os
import sys

import openai

PROMPT = " ".join(sys.argv[1:])
print(PROMPT)

openai.organization = os.getenv("OPENAI_ORG")
openai.api_key = os.getenv("OPENAI_API_KEY")
FINE_TUNED_MODEL = "ft-QWZgrMXPbBkFT4aZwfj03s62"
openai.Completion.create(
    model=FINE_TUNED_MODEL,
    prompt=PROMPT)
