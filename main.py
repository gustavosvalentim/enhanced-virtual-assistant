import logging
import os

from dotenv import load_dotenv
from eva.assistant import EvaAssistant
from eva.tts import TextToSpeech


load_dotenv()

debug = os.getenv('DEBUG', 'False').lower() in ('true', 'yes', '1')
logging.basicConfig(level=logging.DEBUG if debug else logging.ERROR)

model_name = os.getenv('MODEL_NAME', 'openai:gpt-5-mini')
assistant = EvaAssistant(model_name)
tts = TextToSpeech()


def send_assistant_message(message: str):
    print(f'{assistant.assistant_name}: {message}')

    if tts.enabled:
        tts.play(message)


def main():
    print('''
=================
==    E.V.A    ==
=================

type "exit" or press CTRL+C to quit
''')

    while True:
        try:
            query = input('You: ')
        except KeyboardInterrupt:
            print('\n')
            send_assistant_message('Goodbye!')
            break

        if query.lower().strip() == 'exit':
            send_assistant_message('Goodbye!')
            break

        for message in assistant.inference(query):
            send_assistant_message(message)

if __name__ == '__main__':
    main()
