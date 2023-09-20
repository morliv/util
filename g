#!/usr/bin/env python3

import os
import sys
import argparse
import json
from pathlib import Path
from typing import List

import pyperclip
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

def main():
    breakpoint()
    content = ' '.join(content) if (content := sys.argv[1:]) else pyperclip.paste()
    chat = Path("cure.json")
    message = {"role": "user", "content": content}

    completion = openai.ChatCompletion.create(
      model="gpt-4",
      messages=new_message(chat, message))

    new_message(chat.completion.choices[0].message)

def new_message(chat, message) -> List[dict]:
    with chat.open("r") as f:
        file_content = json.load(f)
    if chat.exists() and isinstance(file_content, list):
        file_content.append(message)
    else:
        file_content = [message]
    with chat.open("w") as f:
        json.dump(file_content, f)
    return file_content

if __name__ == '__main__':
    main()

