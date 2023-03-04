import logging
import os
import requests
import telegram
import time
import sys

from dotenv import load_dotenv
from logging import StreamHandler
from http import HTTPStatus
from json import JSONDecodeError


load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
PAYLOAD = {'from_date': 1676246400}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.setLevel(logging.INFO)
    handler = StreamHandler(sys.stdout)
    logger.addHandler(handler)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)


class NoSendMessageException(Exception):
    """Класс исключений отправки сообщений."""


def check_tokens():
    """проверяет доступность переменных окружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN])


def send_message(bot, message):
    """отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Сообщение отправлено успешно')
    except telegram.error.TelegramError as error:
        logger.error(f'Сбой при отправке сообщения: {error}')
        raise NoSendMessageException(f'Сбой при отправке сообщения: {error}')


def get_api_answer(timestamp):
    """делает запрос к эндпоинту API-сервиса."""
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=timestamp)
    except requests.exceptions.RequestException as error:
        raise error('нет ответа сервера либо он не доступен')
    if response.status_code != HTTPStatus.OK:
        raise ValueError(f'Код ответа API не 200, а: {response.status_code}')
    try:
        homework = response.json()
    except JSONDecodeError as error:
        raise error('Ответ API не получилось перевести из формата JSON')
    return homework


def check_response(response):
    """проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError(f'в переменной {response} ожидался словарь')
    if response.get('homeworks') is None:
        raise KeyError('В ответе API нет ключей')
    elif not isinstance(response['homeworks'], list):
        raise TypeError('Получен список вместо ожидаемого словаря')


def parse_status(homework):
    """извлекает статус домашней работы."""
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
    except KeyError as error:
        logger.error(f'В ответе API отсутствуют ключи: {error}')
    if homework_status not in HOMEWORK_VERDICTS:
        logger.error('В ответе API отсутствует staus домашней работы')
        raise KeyError('В ответе API отсутствует staus домашней работы')
    verdict = HOMEWORK_VERDICTS[homework_status]
    return (f'Изменился статус проверки работы "{homework_name}". {verdict}')


def main():
    """Основная логика работы бота."""
    if check_tokens() is False:
        logger.critical('Отсутствуют переменные окружения')
        sys.exit('Отсутствуют переменные окружения')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = PAYLOAD
    error_mesage = ''
    status = ''
    while True:
        try:
            response = get_api_answer(timestamp)
            if response:
                logging.debug(f'отправлен запрос к API: {timestamp}')
            check_response(response)
            if len(response['homeworks']) != 0:
                new_status = parse_status(response['homeworks'][0])
                if new_status != status:
                    send_message(bot, new_status)
                    status = new_status
            current_date = response['current_date']
            timestamp = {'from_date': current_date}
        except Exception as error:
            logger.error(error)
            new_error_mesage = f'Сбой в работе программы: {error}'
            if new_error_mesage != error_mesage:
                send_message(bot, new_error_mesage)
                error_mesage = new_error_mesage
            else:
                logger.error(new_error_mesage)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
