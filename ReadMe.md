[//]: # ()
[//]: # (For a description of the Bot API, see this page: https://core.telegram.org/bots/api)

# Habit Tracker — сервис для формирования полезных привычек

## Описание проекта

Habit Tracker — это веб-приложение для отслеживания и формирования полезных привычек. Сервис помогает пользователям создавать привычки, отмечать их выполнение и получать напоминания в Telegram.

### Основные возможности

- Регистрация и авторизация пользователей (JWT + стандартная Django auth)
- Создание, редактирование и удаление привычек
- Отметка выполнения привычек (трекер)
- Публичные привычки (можно делиться с другими пользователями)
- Автоматические напоминания в Telegram о необходимости выполнить привычку
- Пагинация (5 привычек на страницу)
- API документация (Swagger/ReDoc)

### Технологии

- **Backend:** Django 6.0, Django REST Framework
- **База данных:** PostgreSQL (или SQLite для разработки)
- **Очереди задач:** Celery + Redis
- **Мессенджер:** Telegram Bot API
- **Аутентификация:** JWT (djangorestframework-simplejwt)
- **Документация:** drf-spectacular (Swagger)


## Установка и запуск

### 1. Клонирование репозитория

``` bash
git clone https://github.com/qjlfvfu/SpaProject.git
cd habittracker 
```
### 2. Создание виртуального окружения
bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate      # Windows
3. Установка зависимостей
bash
pip install -r requirements.txt
4. Настройка переменных окружения
Создайте файл .env в корне проекта:

env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=habits_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
5. Применение миграций
bash
python manage.py makemigrations
python manage.py migrate
6. Создание суперпользователя
bash
python manage.py createsuperuser
7. Запуск сервера
bash
python manage.py runserver
Запуск с Docker
bash
docker-compose up -d --build
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
Запуск Celery и Redis
Локально
bash
# Терминал 1 — Redis
redis-server

# Терминал 2 — Celery worker
celery -A config worker -l info

# Терминал 3 — Celery beat (периодические задачи)
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
В Docker
Все сервисы запускаются автоматически через docker-compose up -d

Запуск Telegram бота
bash
python manage.py bot
Бот реагирует на команды:

/start — приветствие

/register <email> — привязка аккаунта

/my_habits — список моих привычек

/today — что нужно сделать сегодня

API Эндпоинты
Аутентификация
Метод	URL	Описание
POST	/api/users/register/	Регистрация
POST	/api/users/login/	Вход (JWT)
POST	/api/users/token/refresh/	Обновление JWT
Привычки
Метод	URL	Описание
GET	/api/habits/	Список моих привычек (пагинация 5)
POST	/api/habits/	Создание привычки
GET	/api/habits/{id}/	Детали привычки
PUT/PATCH	/api/habits/{id}/	Редактирование
DELETE	/api/habits/{id}/	Удаление
GET	/api/habits/public/	Публичные привычки
Трекер выполнения
Метод	URL	Описание
POST	/api/trackers/	Отметить выполнение
GET	/api/trackers/	История выполнения
Telegram привязка
Метод	URL	Описание
POST	/api/users/telegram/	Привязка Telegram chat_id
Документация API
Swagger UI: http://localhost:8000/api/docs/

ReDoc: http://localhost:8000/api/redoc/

Валидации привычек
Время выполнения не более 120 секунд

Периодичность от 1 до 7 дней

Нельзя одновременно указать награду и связанную привычку

Связанная привычка должна быть приятной

У приятной привычки не может быть награды или связанной привычки

Структура проекта
text
SpaProject/
├── config/              # Настройки проекта
├── users/               # Пользователи и аутентификация
├── habittracker/        # Основное приложение (привычки)
│   ├── models.py        # Habit, Tracker
│   ├── views.py         # API представления
│   ├── serializers.py   # DRF сериализаторы
│   ├── permissions.py   # Права доступа
│   ├── paginators.py    # Пагинация
│   ├── tasks.py         # Celery задачи
│   ├── services.py      # Telegram отправка
│   ├── tg_bot.py        # Логика бота
│   └── management/commands/bot.py
├── media/               # Загруженные файлы
├── static/              # Статика
├── .env                 # Переменные окружения
├── docker-compose.yml
├── Dockerfile
└── requirements.txt

Лицензия
~~спросите у дипсика~~
## Контакты
По вопросам: sir.nikolai00@mail.ru