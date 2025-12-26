# Quick Start Guide

Get the Telegram Bar Bot up and running in 5 minutes.

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Telegram Bot Token

## Installation

```bash
# 1. Clone and enter directory
git clone <repository-url>
cd telegram-bar-bot

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings (TELEGRAM_BOT_TOKEN, DATABASE_URL, etc.)

# 5. Setup database
alembic upgrade head
python scripts/init_db.py

# 6. Verify setup
python scripts/verify_setup.py
```

## Running

```bash
# Terminal 1: Start web application
python webapp/main.py

# Terminal 2: Start bot
python bot/main.py
```

## Quick Commands

```bash
# Database migrations
alembic revision --autogenerate -m "description"  # Create migration
alembic upgrade head                               # Apply migrations
alembic downgrade -1                              # Rollback one migration

# Testing
pytest                                            # Run all tests
pytest tests/test_file.py                        # Run specific test

# Development
uvicorn webapp.main:app --reload                 # Run with auto-reload
```

## Project Structure

```
bot/        - Telegram bot handlers
webapp/     - FastAPI web application & Mini App
shared/     - Shared models, config, database
alembic/    - Database migrations
scripts/    - Utility scripts
tests/      - Test files
```

## Key Files

- `.env` - Environment configuration
- `shared/models.py` - Database models
- `shared/config.py` - App configuration
- `bot/main.py` - Bot entry point
- `webapp/main.py` - Web app entry point

## Getting Help

- Full setup guide: See `SETUP.md`
- Project documentation: See `README.md`
- API docs: http://localhost:8000/docs (when running)

## Common Issues

**Import errors?** Activate virtual environment: `source venv/bin/activate`

**Database errors?** Check PostgreSQL is running and DATABASE_URL is correct

**Bot not responding?** Verify TELEGRAM_BOT_TOKEN in `.env`

For detailed troubleshooting, see `SETUP.md`.
