import logging
import sys
from http import HTTPStatus
import time

import requests
import telegram

from exceptions import (
    FalseStatusCodeError,
    RequestError,
)
from settings import (
    ENDPOINT,
    HEADERS,
    PRACTICUM_TOKEN,
    TELEGRAM_CHAT_ID,
    TELEGRAM_TOKEN,
)


RETRY_PERIOD = 600
HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверяет доступность переменных окружения."""
    variables = (PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID,)
    return all(variables)


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
        logging.debug(
            f'Бот отправил сообщение: {message}')
    except telegram.TelegramError as error:
        logging.error(f'Ошибка отправки сообщения: {error}', exc_info=True)


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    payload = {'from_date': timestamp}
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=payload)
        if response.status_code != HTTPStatus.OK:
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


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе статус работы."""
    homework_name = homework.get('homework_name')
    if homework_name is None:
        message = ('Отсутствие ключей в ответе API.')
        logging.error(message, exc_info=True)
        raise KeyError(message)
    status = homework.get('status')
    if status is None:
        logging.error('Статус работы отсутствует', exc_info=True)
    elif status not in HOMEWORK_VERDICTS:
        raise KeyError('Недокументированный статус домашней работы')
    verdict = HOMEWORK_VERDICTS[status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if check_tokens() is False:
        logging.critical(
            'Отсутствует переменная окружения',
            exc_info=True
        )
        sys.exit('Ошибка переменной окружения.')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    previous_message = ''
    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            if [] in response.values():
                message = 'Статус не изменился. Ожидайте.'
            else:
                homework = response['homeworks'][0]
                message = parse_status(homework)
            send_message(bot, message)
            timestamp = response.get('current_date', timestamp)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if message != previous_message:
                send_message(bot, message)
                logging.error(message, exc_info=True)
                previous_message = message
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
    try:
        main()
    except KeyboardInterrupt:
        logging.debug('Программа принудительно остановлена.')
