import os
from functools import lru_cache
from pathlib import Path


PROMPTS_DIR = Path(os.getcwd()) / 'prompts'


@lru_cache(maxsize=32)
def load_prompt(prompt_name: str) -> str:
    with open(PROMPTS_DIR / f'{prompt_name}.txt', 'r') as f:
        prompt = f.read()
        return prompt
