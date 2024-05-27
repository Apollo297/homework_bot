# Check_status_bot

**Описание проекта:**
Телеграм-бота, который проверяет статус домашней работы.

1. Периодический запрос к API сервиса:
   - Каждые 600 секунд (RETRY_PERIOD) бот отправляет запрос к API для получения статуса домашней работы.
2. Проверка и обработка ответа API:
   - Проверяется корректность ответа и его соответствие ожидаемой структуре.
   - Извлекаются данные по домашней работе и анализируется их статус.
3. Отправка сообщений в Telegram:
   - В зависимости от статуса домашней работы бот отправляет соответствующее сообщение в указанный Telegram-чат.
4. Логирование:
   - Используется для ведения журнала событий и ошибок.

   **Библиотеки**
   - requests: для отправки HTTP-запросов к API.
   - logging: для логирования событий и ошибок.
   - telegram: для взаимодействия с Telegram API.
   - time, sys, os, http: стандартные библиотеки для работы с временем, системными операциями и HTTP-статус-кодами.

![image](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![image](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)
![image](https://img.shields.io/badge/VSCode-0078D4?style=for-the-badge&logo=visual%20studio%20code&logoColor=white)
![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)

## Установка:
Если Python не установлен, скачайте и установите его с [официального сайта](https://www.python.org/downloads/).
### Системные требования

- **Версия Python**: 3.9 или выше
- **Операционная система**: Windows / macOS / Linux

Клонировать репозиторий и перейти в него в командной строке:
```python
git clone git@github.com:Apollo297/homework_bot.git
```
```python
cd homework_bot
```
Cоздать и активировать виртуальное окружение:
```python
python3 -m venv env
```
```python
source env/bin/activate
```
Установить зависимости из файла requirements.txt:
```python
python3 -m pip install --upgrade pip
```
```python
pip install -r requirements.txt
```
Запустите скрипт:
```python
python homework.py
```

Если вы запустите этот скрипт, он будет работать в бесконечном цикле, пока вы его принудительно не остановите.

**Автор: Нечепуренко Алексей**
