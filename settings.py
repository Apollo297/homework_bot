import os

from dotenv import load_dotenv

load_dotenv()

ENVIRONMENT_VARIABLES = (
    'PRACTICUM_TOKEN',
    'TELEGRAM_TOKEN',
    'TELEGRAM_CHAT_ID'
)
PRACTICUM_TOKEN = os.getenv(ENVIRONMENT_VARIABLES[0])
TELEGRAM_TOKEN = os.getenv(ENVIRONMENT_VARIABLES[1])
TELEGRAM_CHAT_ID = os.getenv(ENVIRONMENT_VARIABLES[2])


ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
