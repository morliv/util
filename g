#!/usr/bin/env python3

import os
import argparse

import openai
import pyperclip

def main(content):
    openai.api_key = os.getenv("OPENAI_API_KEY")

    completion = openai.ChatCompletion.create(
      model="gpt-4",
      messages=[
        {"role": "user", "content": content}
      ],
      stream=True
    )

    for chunk in completion:
        print(chunk.choices[0].delta)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Chat with GPT-4.')
    parser.add_argument('content', nargs='*', default=pyperclip.paste(), type=str, help='User message content.')
    args = parser.parse_args()
    content = ' '.join(args.content)

    main(content)

