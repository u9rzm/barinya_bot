#!/bin/bash

# Скрипт для очистки всех кешей приложения
# Использование: ./scripts/clear_cache.sh [--force]

set -e

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

FORCE=false
if [[ "$1" == "--force" ]]; then
    FORCE=true
fi

echo -e "${YELLOW}🧹 Очистка кешей приложения...${NC}"

# Проверяем, запущен ли Docker Compose
if ! docker-compose ps | grep -q "Up"; then
    echo -e "${RED}❌ Docker Compose не запущен!${NC}"
    echo -e "${YELLOW}Запустите 'make up' сначала${NC}"
    exit 1
fi

# 1. Очистка кеша nginx
echo -e "${YELLOW}📦 Очистка кеша nginx...${NC}"
if docker-compose ps nginx | grep -q "Up"; then
    # Очищаем кеш nginx (если есть)
    docker-compose -f $(COMPOSE_FILE) exec nginx sh -c "find /var/cache/nginx -type f -delete 2>/dev/null || true"
    
    # Проверяем конфигурацию и перезагружаем
    if docker-compose -f $(COMPOSE_FILE) exec nginx nginx -t >/dev/null 2>&1; then
        docker-compose -f $(COMPOSE_FILE) exec nginx nginx -s reload
        echo -e "${GREEN}✅ Кеш nginx очищен${NC}"
    else
        echo -e "${RED}❌ Ошибка в конфигурации nginx!${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️ Nginx не запущен, пропускаем${NC}"
fi

# 2. Очистка кеша приложения (если есть)
echo -e "${YELLOW}🐍 Очистка кеша Python...${NC}"
if docker-compose ps webapp | grep -q "Up"; then
    # Очищаем __pycache__ файлы
    docker-compose exec webapp find /app -name "*.pyc" -delete 2>/dev/null || true
    docker-compose exec webapp find /app -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    echo -e "${GREEN}✅ Кеш Python очищен${NC}"
else
    echo -e "${YELLOW}⚠️ Webapp не запущен, пропускаем${NC}"
fi

# 3. Генерация нового cache-busting timestamp для статических файлов
echo -e "${YELLOW}🌐 Обновление версии статических файлов...${NC}"
TIMESTAMP=$(date +%s)

# Создаем файл с версией для использования в приложении
if docker-compose ps webapp | grep -q "Up"; then
    docker-compose exec webapp sh -c "echo '$TIMESTAMP' > /app/static_version.txt"
    # Также создаем файл в статической папке для прямого доступа
    docker-compose exec webapp sh -c "echo '$TIMESTAMP' > /app/webapp/static/version.txt"
    echo -e "${GREEN}✅ Версия статических файлов обновлена: $TIMESTAMP${NC}"
else
    echo -e "${YELLOW}⚠️ Webapp не запущен, создаем локальный файл версии${NC}"
    echo "$TIMESTAMP" > webapp/static/version.txt
fi

# 4. Опционально - перезапуск сервисов для полной очистки
if [[ "$FORCE" == "true" ]]; then
    echo -e "${YELLOW}🔄 Принудительный перезапуск сервисов...${NC}"
    docker-compose restart webapp bot
    echo -e "${GREEN}✅ Сервисы перезапущены${NC}"
fi

echo -e "${GREEN}🎉 Очистка кешей завершена!${NC}"
echo -e "${YELLOW}💡 Для принудительного перезапуска используйте: $0 --force${NC}"

# Показываем статус
echo -e "\n${GREEN}📊 Текущий статус сервисов:${NC}"
docker-compose ps