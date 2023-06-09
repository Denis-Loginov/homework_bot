# Проект «Homework Bot»
## Описание проекта
Проект **Homework Bot** имеет функционал Telegram-бота, взаиможействующего с API сервиса Практикум.Домашка и узнаюего статус домашней работы (не взята на проверку, взята на ревью, принята ревьювером либо возвращена на доработку)

Telegram-бот работает по правилам:

- раз в 10 минут узнает статус;

- при обновлении статуса анализирует ответ API и отправляет уведомление в Telegram;

- логирует свою работу и сообщать о проблемах сообщением в Telegram.

## Технологии
<img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue" />
<img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green" />
<img src="https://img.shields.io/badge/django%20rest-ff1709?style=for-the-badge&logo=django&logoColor=white" />

## Установка

Клонировать репозиторий с GitHub.

Установить вертуальное окружение.
```
python -m venv venv
```

Активировать вертуальное окружение.
```
source venv/scripts/activate
```

Установить зависимости из requirements.txt.
```
python pip install -r requirements.txt
```

Выполнить миграции.
```
python manage.py makemigrations
python manage.py migrate
```

Запустить сервер.
```
python manage.py runserver
```
