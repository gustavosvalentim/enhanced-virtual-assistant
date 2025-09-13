import logging
import os

from dotenv import load_dotenv
from eva.assistant import EvaAssistant


load_dotenv()


debug = os.getenv('DEBUG', 'False').lower() in ('true', 'yes', '1')
logging.basicConfig(level=logging.DEBUG if debug else logging.WARNING)

assistant = EvaAssistant()


def send_assistant_message(message: str):
    print(f'{assistant.assistant_name}: {message}')


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
