# Telegram Bar Bot - Setup Guide

This guide will walk you through setting up the Telegram Bar Bot project from scratch.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11 or higher**
- **PostgreSQL 15+**
- **pip** (Python package manager)
- **Git** (for version control)

## Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd telegram-bar-bot
```

### 2. Create Virtual Environment

It's recommended to use a virtual environment to isolate project dependencies:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

Install all required Python packages:

```bash
pip install -r requirements.txt
```

Or using pyproject.toml:

```bash
pip install -e .
```

### 4. Set Up PostgreSQL Database

Create a PostgreSQL database for the project:

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE telegram_bar_bot;

# Create user (optional)
CREATE USER barbot WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE telegram_bar_bot TO barbot;

# Exit psql
\q
```

### 5. Configure Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` file with your configuration:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_WEBHOOK_URL=https://your-domain.com/webhook

# Database Configuration
DATABASE_URL=postgresql+asyncpg://barbot:your_password@localhost:5432/telegram_bar_bot

# Admin Configuration (comma-separated telegram IDs)
ADMIN_TELEGRAM_IDS=123456789,987654321

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=False

# Logging
LOG_LEVEL=INFO
```

#### Getting Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the token provided by BotFather
5. Paste it in your `.env` file as `TELEGRAM_BOT_TOKEN`

#### Finding Your Telegram ID

1. Open Telegram and search for [@userinfobot](https://t.me/userinfobot)
2. Send `/start` command
3. The bot will reply with your Telegram ID
4. Add this ID to `ADMIN_TELEGRAM_IDS` in `.env`

### 6. Verify Project Setup

Run the verification script to ensure everything is configured correctly:

```bash
python scripts/verify_setup.py
```

This will check:
- Project directory structure
- Configuration files
- Python modules
- Database migrations

### 7. Initialize Database

Run database migrations to create all tables:

```bash
# Apply migrations
alembic upgrade head
```

Create initial seed data (loyalty levels and menu categories):

```bash
python scripts/init_db.py
```

This will create:
- 4 loyalty levels (Bronze, Silver, Gold, Platinum)
- 5 menu categories (Напитки, Коктейли, Закуски, Горячие блюда, Десерты)

### 8. Run the Application

#### Start the Web Application (FastAPI)

In one terminal:

```bash
python webapp/main.py
```

Or with uvicorn for development:

```bash
uvicorn webapp.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: http://localhost:8000

API documentation: http://localhost:8000/docs

#### Start the Telegram Bot

In another terminal:

```bash
python bot/main.py
```

### 9. Test the Bot

1. Open Telegram
2. Search for your bot by username
3. Send `/start` command
4. The bot should respond with a welcome message

## Project Structure

```
telegram-bar-bot/
├── bot/                    # Telegram bot
│   ├── __init__.py
│   └── main.py            # Bot entry point
├── webapp/                 # FastAPI web application
│   ├── __init__.py
│   ├── main.py            # Web app entry point
│   ├── static/            # Static files (CSS, JS, images)
│   └── templates/         # Jinja2 templates for Mini App
├── shared/                 # Shared code between bot and webapp
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── database.py        # Database connection and session
│   └── models.py          # SQLAlchemy models
├── alembic/               # Database migrations
│   ├── versions/          # Migration files
│   ├── env.py            # Alembic environment
│   └── script.py.mako    # Migration template
├── scripts/               # Utility scripts
│   ├── init_db.py        # Database initialization
│   └── verify_setup.py   # Setup verification
├── tests/                 # Tests
│   ├── __init__.py
│   └── conftest.py       # Pytest configuration
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
├── alembic.ini          # Alembic configuration
├── pyproject.toml       # Project metadata and dependencies
├── requirements.txt     # Python dependencies
├── README.md           # Project documentation
└── SETUP.md            # This file
```

## Database Schema

The application uses the following main tables:

- **users** - User accounts with Telegram info
- **loyalty_levels** - Loyalty program levels
- **points_transactions** - Points transaction history
- **orders** - User orders
- **order_items** - Items in orders
- **menu_items** - Bar menu items
- **menu_categories** - Menu categories
- **promotions** - Promotional campaigns

## Development Workflow

### Creating a New Migration

When you modify models in `shared/models.py`:

```bash
# Generate migration
alembic revision --autogenerate -m "description of changes"

# Review the generated migration in alembic/versions/

# Apply migration
alembic upgrade head
```

### Rolling Back Migrations

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Rollback all migrations
alembic downgrade base
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_specific.py
```

## Troubleshooting

### Database Connection Issues

If you get database connection errors:

1. Check PostgreSQL is running:
   ```bash
   sudo systemctl status postgresql
   ```

2. Verify database exists:
   ```bash
   psql -U postgres -l
   ```

3. Check DATABASE_URL in `.env` is correct

### Bot Not Responding

1. Verify TELEGRAM_BOT_TOKEN is correct in `.env`
2. Check bot is running without errors
3. Ensure bot is not blocked by user
4. Check logs for error messages

### Import Errors

If you get import errors:

1. Ensure virtual environment is activated
2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Check Python version:
   ```bash
   python --version  # Should be 3.11+
   ```

## Next Steps

After setup is complete:

1. **Implement Bot Handlers** - Add command handlers in `bot/`
2. **Create API Endpoints** - Add REST endpoints in `webapp/`
3. **Design Mini App UI** - Create Jinja2 templates in `webapp/templates/`
4. **Add Business Logic** - Implement services for loyalty, referrals, etc.
5. **Write Tests** - Add unit and integration tests in `tests/`

## Additional Resources

- [aiogram Documentation](https://docs.aiogram.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Telegram Mini Apps](https://core.telegram.org/bots/webapps)

## Support

For issues or questions, please refer to the project documentation or create an issue in the repository.
