# Руководство по развертыванию Telegram Bar Bot

Это подробное руководство по развертыванию системы в продакшене.

## Предварительные требования

### Сервер

- **ОС**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **RAM**: минимум 2GB, рекомендуется 4GB+
- **Диск**: минимум 20GB свободного места
- **CPU**: 2+ ядра
- **Сеть**: публичный IP адрес

### Программное обеспечение

- Docker 20.10+
- Docker Compose 2.0+
- Git
- Nginx (опционально, если не используете Docker Compose)

### Внешние сервисы

- **Домен**: зарегистрированный домен с настроенными DNS записями
- **Telegram Bot**: токен от @BotFather
- **SSL сертификат**: Let's Encrypt или коммерческий

## Пошаговое развертывание

### Шаг 1: Подготовка сервера

```bash
# Обновить систему
sudo apt update && sudo apt upgrade -y

# Установить Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Установить Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Перелогиниться для применения группы docker
exit
# Войти снова по SSH
```

### Шаг 2: Клонирование и настройка

```bash
# Клонировать репозиторий
git clone <repository-url>
cd telegram-bar-bot

# Создать конфигурацию
cp .env.production .env

# Отредактировать конфигурацию
nano .env
```

### Шаг 3: Настройка окружения

Отредактируйте `.env` файл:

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_WEBHOOK_URL=https://your-domain.com/webhook

# База данных
POSTGRES_PASSWORD=very_secure_password_here

# Администраторы (получить ID можно у @userinfobot)
ADMIN_TELEGRAM_IDS=123456789,987654321

# Приложение
DEBUG=False
LOG_LEVEL=INFO
```

### Шаг 4: Настройка DNS

Настройте A-запись для вашего домена:

```
your-domain.com.    IN    A    YOUR_SERVER_IP
```

Проверьте настройку:

```bash
nslookup your-domain.com
```

### Шаг 5: Развертывание

```bash
# Автоматическое развертывание
./scripts/deploy.sh your-domain.com admin@your-domain.com

# Или пошагово:

# 1. Настроить SSL
./scripts/setup_ssl.sh your-domain.com admin@your-domain.com

# 2. Собрать и запустить сервисы
docker-compose build
docker-compose up -d postgres
sleep 10
docker-compose run --rm webapp alembic upgrade head
docker-compose up -d

# 3. Настроить webhook
docker-compose exec webapp python scripts/setup_webhook.py set
```

### Шаг 6: Проверка развертывания

```bash
# Проверить статус сервисов
docker-compose ps

# Проверить логи
docker-compose logs -f

# Проверить webhook
docker-compose exec webapp python scripts/setup_webhook.py info

# Проверить доступность
curl -k https://your-domain.com/health
```

## Настройка Let's Encrypt

### Автоматическая настройка

```bash
# Установить certbot
sudo apt install certbot

# Остановить nginx
docker-compose stop nginx

# Получить сертификат
sudo certbot certonly --standalone -d your-domain.com --email admin@your-domain.com --agree-tos --non-interactive

# Скопировать сертификаты
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./ssl/key.pem
sudo chown $(whoami):$(whoami) ./ssl/*.pem

# Запустить nginx
docker-compose up -d nginx
```

### Автоматическое обновление

```bash
# Добавить в crontab
sudo crontab -e

# Добавить строку:
0 12 * * * /usr/bin/certbot renew --quiet --deploy-hook "cd /path/to/telegram-bar-bot && docker-compose restart nginx"
```

## Мониторинг и обслуживание

### Настройка логирования

```bash
# Настроить ротацию логов
sudo nano /etc/logrotate.d/telegram-bar-bot
```

Содержимое файла:

```
/path/to/telegram-bar-bot/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker-compose restart webapp
    endscript
}
```

### Мониторинг ресурсов

```bash
# Использование ресурсов контейнерами
docker stats

# Размер логов
du -sh logs/

# Использование диска
df -h

# Использование памяти
free -h
```

### Резервное копирование

Создайте скрипт резервного копирования:

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/telegram-bar-bot"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Бэкап базы данных
docker-compose exec -T postgres pg_dump -U barbot telegram_bar_bot > $BACKUP_DIR/db_$DATE.sql

# Бэкап конфигурации
cp .env $BACKUP_DIR/env_$DATE
cp -r ssl $BACKUP_DIR/ssl_$DATE

# Удалить старые бэкапы (старше 30 дней)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "env_*" -mtime +30 -delete
find $BACKUP_DIR -name "ssl_*" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR"
```

Добавьте в crontab:

```bash
# Ежедневный бэкап в 2:00
0 2 * * * /path/to/telegram-bar-bot/backup.sh
```

## Обновление системы

### Обновление кода

```bash
# Остановить сервисы
docker-compose down

# Обновить код
git pull origin main

# Пересобрать и запустить
docker-compose build --no-cache
docker-compose up -d postgres
sleep 10
docker-compose run --rm webapp alembic upgrade head
docker-compose up -d

# Проверить статус
docker-compose ps
```

### Обновление зависимостей

```bash
# Обновить requirements.txt
# Пересобрать образ
docker-compose build --no-cache webapp

# Перезапустить
docker-compose up -d webapp
```

## Безопасность

### Настройка файрвола

```bash
# Установить ufw
sudo apt install ufw

# Базовые правила
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Разрешить SSH
sudo ufw allow ssh

# Разрешить HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Включить файрвол
sudo ufw enable
```

### Настройка fail2ban

```bash
# Установить fail2ban
sudo apt install fail2ban

# Создать конфигурацию
sudo nano /etc/fail2ban/jail.local
```

Содержимое:

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true
logpath = /var/log/nginx/error.log
```

### Регулярные обновления безопасности

```bash
# Автоматические обновления безопасности
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## Устранение неполадок

### Проблемы с SSL

```bash
# Проверить сертификат
openssl x509 -in ssl/cert.pem -text -noout

# Проверить приватный ключ
openssl rsa -in ssl/key.pem -check

# Тест SSL соединения
openssl s_client -connect your-domain.com:443
```

### Проблемы с базой данных

```bash
# Проверить подключение к БД
docker-compose exec postgres psql -U barbot -d telegram_bar_bot -c "SELECT version();"

# Проверить размер БД
docker-compose exec postgres psql -U barbot -d telegram_bar_bot -c "SELECT pg_size_pretty(pg_database_size('telegram_bar_bot'));"

# Восстановить из бэкапа
docker-compose exec -T postgres psql -U barbot telegram_bar_bot < backup.sql
```

### Проблемы с webhook

```bash
# Проверить доступность webhook URL
curl -X POST https://your-domain.com/webhook -H "Content-Type: application/json" -d '{}'

# Проверить логи Telegram
docker-compose exec webapp python scripts/setup_webhook.py info

# Переустановить webhook
docker-compose exec webapp python scripts/setup_webhook.py delete
docker-compose exec webapp python scripts/setup_webhook.py set
```

## Масштабирование

### Горизонтальное масштабирование

Для высоких нагрузок можно развернуть несколько экземпляров:

```yaml
# docker-compose.scale.yml
version: '3.8'

services:
  webapp:
    deploy:
      replicas: 3
    
  nginx:
    depends_on:
      - webapp
    volumes:
      - ./nginx.scale.conf:/etc/nginx/nginx.conf:ro
```

### Мониторинг производительности

```bash
# Установить мониторинг
docker run -d --name prometheus prom/prometheus
docker run -d --name grafana grafana/grafana

# Настроить метрики в приложении
# Добавить prometheus_client в requirements.txt
```

## Поддержка

При возникновении проблем:

1. Проверьте логи: `docker-compose logs -f`
2. Проверьте статус сервисов: `docker-compose ps`
3. Проверьте webhook: `python scripts/setup_webhook.py info`
4. Проверьте SSL сертификат: `openssl x509 -in ssl/cert.pem -dates -noout`

Для получения помощи создайте issue в репозитории с подробным описанием проблемы и логами.