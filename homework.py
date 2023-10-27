import logging
import os
import sys
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

ERROR_MESSAGE = ''

PRACTICUM_TOKEN = os.getenv('PRAC_TOKEN')
TELEGRAM_TOKEN = os.getenv('TEL_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TEL_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


class FalseStatusCodeError(Exception):
    """Статус ошибки доступа к эндпоинту."""


class RequestError(Exception):
    """Ошибка запроса."""


class UnexpectedStatusError(Exception):
    """Неожиданный статус домашней работы."""


class MessageError(Exception):
    """Ошибка отправки сообщения."""


class VariableError(Exception):
    """Ошибка переменной окружения."""


def check_tokens():
    """Проверяет доступность переменных окружения."""
    if PRACTICUM_TOKEN is None:
        logging.critical(PRACTICUM_TOKEN, exc_info=True)
        return False
    if TELEGRAM_TOKEN is None:
        logging.critical(TELEGRAM_TOKEN, exc_info=True)
        return False
    if TELEGRAM_CHAT_ID is None:
        logging.critical(TELEGRAM_CHAT_ID, exc_info=True)
        return False
    return True


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
        logging.debug(
            f'Бот отправил сообщение: {message}')
    except Exception as error:
        logging.error(f'Ошибка отправки сообщения: {error}', exc_info=True)
        raise MessageError(error)


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    payload = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
        if response.status_code != 200:
            message = (
                f'Эндпоинт {ENDPOINT} недоступен.'
                f'Код ответа API: {response.status_code}'
            )
            logging.error(message)
            raise FalseStatusCodeError(message)
        return response.json()
    except requests.exceptions.RequestException as error:
        logging.error(f'Ошибка при запросе к API: {error}', exc_info=True)
        raise RequestError(error)


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        message = 'response не является словарем.'
        raise TypeError(message)
    if 'homeworks' not in response:
        message = 'В ответе API домашки нет ключа "homeworks".'
        raise KeyError(message)
    homeworks = response['homeworks']
    if not isinstance(homeworks, list):
        message = 'response не явлляется списком.'
        raise TypeError(message)
    return response['homeworks'][0]


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе статус работы."""
    homework_name = homework.get('homework_name')
    if homework_name is None:
        message = ('Отсутствие ключей в ответе API.')
        logging.error(message)
        raise KeyError(message)
    status = homework.get('status')
    if status not in HOMEWORK_VERDICTS:
        raise KeyError('Недокументированный статус домашней работы')
    verdict = HOMEWORK_VERDICTS[status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def sending_identical_messages(message):
    """Ограничение на отправку повторных сообщений об ошибке."""
    return message != ERROR_MESSAGE


def main():
    """Основная логика работы бота."""
    if check_tokens() is False:
        raise VariableError('Ошибка переменной окружения.')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            message = parse_status(homework)
            send_message(bot, message)
            timestamp = response.get('current_date', timestamp)
        except IndexError:
            message = 'Статус не изменился. Ожидайте.'
            send_message(bot, message)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if sending_identical_messages(message):
                send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        encoding='utf-8',
        format='%(asctime)s, %(levelname)s, %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(
                filename='program.log',
                mode='w',
                encoding='utf-8'
            )
        ]
    )
    main()
