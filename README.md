# Telegram Bar Bot

Система Telegram бота для бара с программой лояльности, реферальной системой и мини-приложением с меню.

## Возможности

- 🤖 **Telegram Bot** - взаимодействие с пользователями через команды
- 📱 **Mini App** - веб-приложение с меню бара, встроенное в Telegram
- 🎁 **Система лояльности** - накопление баллов и уровни пользователей
- 👥 **Реферальная система** - приглашение друзей с вознаграждениями
- 📊 **Статистика** - история заказов, транзакций и рефералов
- 🔔 **Рассылки** - уведомления о промо-акциях
- 👨‍💼 **Админ-панель** - управление меню, акциями и пользователями

## Технологический стек

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, Alembic
- **Bot**: aiogram 3.x для работы с Telegram Bot API
- **Database**: PostgreSQL 15+
- **Frontend**: Jinja2 шаблоны, Telegram Web App SDK, TailwindCSS
- **Deployment**: Docker, Docker Compose, Nginx
- **SSL**: Let's Encrypt / самоподписанные сертификаты

## Project Structure

```
.
├── bot/                    # Telegram bot handlers
├── webapp/                 # FastAPI web application
├── shared/                 # Shared code (models, config, database)
├── alembic/               # Database migrations
├── tests/                 # Tests
├── requirements.txt       # Python dependencies
├── pyproject.toml        # Project configuration
└── .env                  # Environment variables (create from .env.example)
```

## Быстрый старт

### 🚀 Продакшен за 5 минут

```bash
# 1. Клонируйте репозиторий
git clone <repository-url>
cd telegram-bar-bot

# 2. Настройте окружение
cp .env.production .env
nano .env  # Укажите TELEGRAM_BOT_TOKEN и другие настройки

# 3. Разверните одной командой
./scripts/deploy.sh your-domain.com admin@your-domain.com
```

**Готово!** Ваш бот работает на `https://your-domain.com`

### 💻 Разработка локально

```bash
# 1. Установите зависимости
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Настройте базу данных
createdb telegram_bar_bot
alembic upgrade head

# 3. Запустите приложение
uvicorn webapp.main:app --reload &
python -m bot.main
```

### Требования

- **Docker** и **Docker Compose** (для продакшена)
- **Python 3.11+** (для разработки)
- **PostgreSQL 15+** (если не используете Docker)
- **Telegram Bot Token** (получить у @BotFather)
- **Домен с SSL** (для продакшена)

### Разработка (локально)

1. **Создайте виртуальное окружение:**
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

3. **Настройте базу данных:**
```bash
# Создайте PostgreSQL базу данных
createdb telegram_bar_bot

# Выполните миграции
alembic upgrade head

# Инициализируйте начальные данные
python scripts/init_db.py
```

4. **Настройте окружение:**
```bash
cp .env.example .env
# Отредактируйте .env с вашими настройками
```

5. **Запустите приложение:**
```bash
# Веб-приложение
uvicorn webapp.main:app --host 0.0.0.0 --port 8000 --reload

# В отдельном терминале - бот
python -m bot.main
```

## Команды бота

### Пользовательские команды
- `/start [referral_code]` - Регистрация и начало работы с ботом
- `/menu` - Открыть меню в Mini App
- `/profile` - Посмотреть свой профиль
- `/referral` - Получить реферальную ссылку
- `/help` - Показать справку по командам

### Административные команды
- `/admin_add_item` - Добавить позицию в меню
- `/admin_edit_item` - Редактировать позицию меню
- `/admin_create_promo` - Создать промо-акцию
- `/admin_broadcast` - Отправить рассылку всем пользователям
- `/admin_set_level <username> <level>` - Назначить уровень лояльности пользователю

## Переменные окружения

### Обязательные настройки

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here          # Токен бота от @BotFather
TELEGRAM_WEBHOOK_URL=https://your-domain.com/webhook  # URL для webhook

# База данных
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/telegram_bar_bot
POSTGRES_PASSWORD=secure_password_here          # Пароль для Docker PostgreSQL

# Администраторы
ADMIN_TELEGRAM_IDS=123456789,987654321         # ID администраторов через запятую
```

### Дополнительные настройки

```bash
# Приложение
APP_HOST=0.0.0.0                               # Хост для FastAPI
APP_PORT=8000                                  # Порт для FastAPI
DEBUG=False                                    # Режим отладки
LOG_LEVEL=INFO                                 # Уровень логирования

# Google Sheets (опционально)
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id
GOOGLE_SHEETS_RANGE=Menu!A2:F

# Webhook безопасность (опционально)
WEBHOOK_SECRET_TOKEN=your_secret_token_here
```

## Управление сервисами

### Docker команды

```bash
# Просмотр статуса сервисов
docker-compose ps

# Просмотр логов
docker-compose logs -f
docker-compose logs -f webapp  # Только веб-приложение
docker-compose logs -f postgres  # Только база данных

# Перезапуск сервисов
docker-compose restart
docker-compose restart webapp

# Остановка сервисов
docker-compose down

# Полная очистка (удаляет данные!)
docker-compose down -v
```

### Управление webhook

```bash
# Установить webhook
docker-compose exec webapp python scripts/setup_webhook.py set

# Проверить статус webhook
docker-compose exec webapp python scripts/setup_webhook.py info

# Удалить webhook
docker-compose exec webapp python scripts/setup_webhook.py delete
```

### Работа с базой данных

```bash
# Подключиться к базе данных
docker-compose exec postgres psql -U barbot -d telegram_bar_bot

# Выполнить миграции
docker-compose exec webapp alembic upgrade head

# Создать новую миграцию
docker-compose exec webapp alembic revision --autogenerate -m "description"

# Инициализировать начальные данные
docker-compose exec webapp python scripts/init_db.py
```

## Архитектура системы

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Пользователь  │────│  Telegram API    │────│   Aiogram Bot   │
│    Telegram     │    │                  │    │   (Webhook)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         │ REST API
                                                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Mini App      │────│     Nginx        │────│  FastAPI App    │
│  (Jinja2 +     │    │  (SSL + Proxy)   │    │   + Services    │
│   Web App SDK)  │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         │ SQLAlchemy
                                                         ▼
                                               ┌─────────────────┐
                                               │   PostgreSQL    │
                                               │    Database     │
                                               └─────────────────┘
```

## Разработка

### Запуск тестов

```bash
# Все тесты
pytest

# Только unit тесты
pytest tests/test_services.py

# Property-based тесты
pytest tests/ -k "property"

# С покрытием кода
pytest --cov=shared --cov=bot --cov=webapp
```

### Создание миграций

```bash
# Автоматическая миграция на основе изменений моделей
alembic revision --autogenerate -m "add new table"

# Пустая миграция для ручного редактирования
alembic revision -m "custom migration"

# Применить миграции
alembic upgrade head

# Откатить миграцию
alembic downgrade -1
```

### Отладка

```bash
# Логи в реальном времени
docker-compose logs -f webapp

# Подключиться к контейнеру
docker-compose exec webapp bash

# Проверить состояние webhook
curl -X GET "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getWebhookInfo"

# Тестовый запрос к API
curl -X GET "https://your-domain.com/health"
```

## Мониторинг и обслуживание

### Логи

Логи сохраняются в папке `logs/`:
- `app.log` - основные логи приложения
- `error.log` - ошибки
- `access.log` - HTTP запросы

### Резервное копирование

```bash
# Создать бэкап базы данных
docker-compose exec postgres pg_dump -U barbot telegram_bar_bot > backup.sql

# Восстановить из бэкапа
docker-compose exec -T postgres psql -U barbot telegram_bar_bot < backup.sql
```

### Обновление SSL сертификатов

```bash
# Обновить Let's Encrypt сертификаты
sudo certbot renew

# Скопировать новые сертификаты
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./ssl/key.pem

# Перезапустить nginx
docker-compose restart nginx
```

## Устранение неполадок

### Частые проблемы

1. **Webhook не работает**
   ```bash
   # Проверить статус webhook
   python scripts/setup_webhook.py info
   
   # Переустановить webhook
   python scripts/setup_webhook.py set
   ```

2. **База данных недоступна**
   ```bash
   # Проверить статус PostgreSQL
   docker-compose ps postgres
   
   # Перезапустить базу данных
   docker-compose restart postgres
   ```

3. **SSL сертификат истек**
   ```bash
   # Обновить сертификаты Let's Encrypt
   sudo certbot renew --deploy-hook "docker-compose restart nginx"
   ```

4. **Бот не отвечает**
   ```bash
   # Проверить логи бота
   docker-compose logs webapp
   
   # Перезапустить приложение
   docker-compose restart webapp
   ```

### Полезные ссылки

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Telegram Web Apps](https://core.telegram.org/bots/webapps)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Docker Compose](https://docs.docker.com/compose/)

## Лицензия

MIT License - см. файл LICENSE для деталей.
