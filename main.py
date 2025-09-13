import logging
import os

from dotenv import load_dotenv
from jarvis.agent import JarvisAgent


load_dotenv()

debug = os.getenv('DEBUG', 'False').lower() in ('true', 'yes', '1')
logging.basicConfig(level=logging.DEBUG if debug else logging.WARNING)


def main():
    agent = JarvisAgent()

    print("Jarvis: How can I assist you? (type 'exit' to quit)")

    while True:
        try:
            query = input('You: ')
        except KeyboardInterrupt:
            print('\n')
            print('Jarvis: Goodbye!')
            break

        if query.lower().strip() == 'exit':
            print('Jarvis: Goodbye!')
            break

        for message in agent.inference(query):
            print('Jarvis:', message)

if __name__ == '__main__':
    main()
