# Makefile for Telegram Bar Bot
# Управление Docker Compose приложением
include make/base.mk
ENV ?= dev

ifeq ($(ENV),dev)
include make/dev.mk
endif

ifeq ($(ENV),prod)
include make/prod.mk
endif

# Запуск всех сервисов
.PHONY: up
up: check-env
	@echo "$(GREEN)Запуск всех сервисов...$(NC)"
	docker-compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) up -d
	@echo "$(GREEN)Сервисы запущены!$(NC)"
	@make status

# Остановка всех сервисов
.PHONY: down
down:
	@echo "$(YELLOW)Остановка всех сервисов...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down
	@echo "$(GREEN)Сервисы остановлены!$(NC)"

# Перезапуск всех сервисов
.PHONY: restart
restart: down up

# Пересборка и запуск приложения
.PHONY: rebuild
rebuild: check-env
	@echo "$(GREEN)Пересборка и запуск приложения...$(NC)"
	@echo "$(YELLOW)Очистка кеша nginx...$(NC)"
# 	@make clear-nginx-cache
	docker-compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) up -d --build
	@echo "$(GREEN)Приложение пересобрано и запущено!$(NC)"
	@make status

# Пересборка только webapp и bot
.PHONY: rebuild-app
rebuild-app: check-env
	@echo "$(GREEN)Пересборка webapp и bot...$(NC)"
	@echo "$(YELLOW)Очистка кеша nginx...$(NC)"
# 	@make clear-nginx-cache
	docker-compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) up -d --build webapp bot
	@echo "$(GREEN)Приложения пересобраны!$(NC)"
	@make status

# Просмотр логов
.PHONY: logs
logs:
	docker-compose -f $(COMPOSE_FILE) logs -f

.PHONY: logs-app
logs-app:
	docker-compose -f $(COMPOSE_FILE) logs -f webapp

.PHONY: logs-bot
logs-bot:
	docker-compose -f $(COMPOSE_FILE) logs -f bot

.PHONY: logs-db
logs-db:
	docker-compose -f $(COMPOSE_FILE) logs -f postgres

.PHONY: logs-nginx
logs-nginx:
	docker-compose -f $(COMPOSE_FILE) logs -f nginx


# Статус сервисов
.PHONY: status
status:
	@echo "$(GREEN)Статус сервисов:$(NC)"
	docker-compose -f $(COMPOSE_FILE) ps

# Очистка
.PHONY: clean
clean:
	@echo "$(YELLOW)Очистка контейнеров и сетей...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down --remove-orphans
	docker system prune -f
	@echo "$(GREEN)Очистка завершена!$(NC)"

.PHONY: clean-all
clean-all:
	@echo "$(RED)ВНИМАНИЕ: Это удалит ВСЕ данные включая базу данных!$(NC)"
	@read -p "Вы уверены? (y/N): " confirm && [ "$$confirm" = "y" ]
	docker-compose -f $(COMPOSE_FILE) down -v --remove-orphans
	docker system prune -a -f --volumes
	@echo "$(GREEN)Полная очистка завершена!$(NC)"

# Подключение к контейнерам
.PHONY: shell-app
shell-app:
	docker-compose -f $(COMPOSE_FILE) exec webapp /bin/bash

.PHONY: shell-bot
shell-bot:
	docker-compose -f $(COMPOSE_FILE) exec bot /bin/bash

.PHONY: shell-db
shell-db:
	docker-compose -f $(COMPOSE_FILE) exec postgres psql -U barbot -d telegram_bar_bot

# Работа с базой данных
.PHONY: db-migrate
db-migrate:
	@echo "$(GREEN)Выполнение миграций...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec webapp alembic upgrade head
	@echo "$(GREEN)Миграции выполнены!$(NC)"

.PHONY: db-init
db-init:
	@echo "$(GREEN)Инициализация базы данных с начальными данными...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec webapp python -c "import sys; sys.path.append('/app'); from scripts.init_db import main; import asyncio; asyncio.run(main())"
	@echo "$(GREEN)База данных инициализирована!$(NC)"

.PHONY: db-reset
db-reset:
	@echo "$(RED)ВНИМАНИЕ: Это удалит ВСЕ данные из базы!$(NC)"
	@read -p "Вы уверены? (y/N): " confirm && [ "$$confirm" = "y" ]
	docker-compose -f $(COMPOSE_FILE) stop webapp bot
	docker-compose -f $(COMPOSE_FILE) exec postgres psql -U barbot -d telegram_bar_bot -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	@make db-migrate
	docker-compose -f $(COMPOSE_FILE) start webapp bot
	@echo "$(GREEN)База данных сброшена!$(NC)"

# Быстрые команды для разработки
.PHONY: dev
dev: rebuild logs

.PHONY: prod
prod: check-env up

# Быстрый деплой с очисткой кеша
.PHONY: deploy
deploy: check-env
	@echo "$(GREEN)🚀 Быстрый деплой с очисткой кеша...$(NC)"
	@make clear-nginx-cache
	docker-compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) up -d --build --force-recreate webapp bot
	@echo "$(GREEN)✅ Деплой завершен!$(NC)"
	@make status

# Деплой только фронтенда (статические файлы + webapp)
.PHONY: deploy-frontend
deploy-frontend: check-env
	@echo "$(GREEN)🎨 Деплой фронтенда...$(NC)"
	@make clear-nginx-cache
	docker-compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) up -d --build webapp
	@echo "$(GREEN)✅ Фронтенд обновлен!$(NC)"

# По умолчанию показываем help
.DEFAULT_GOAL := help

# Тестирование статических файлов
.PHONY: test-static
test-static:
	@echo "$(GREEN)Тестирование статических файлов...$(NC)"
	./scripts/test_static.sh

# Очистка кеша nginx
.PHONY: clear-nginx-cache
clear-nginx-cache:
	@echo "$(YELLOW)Очистка кеша nginx...$(NC)"
	@./scripts/clear_cache.sh

# Принудительная очистка всех кешей
.PHONY: clear-cache-force
clear-cache-force:
	@echo "$(YELLOW)Принудительная очистка всех кешей...$(NC)"
	@./scripts/clear_cache.sh --force

# Перезагрузка nginx без остановки
.PHONY: reload-nginx
reload-nginx:
	@echo "$(YELLOW)Перезагрузка конфигурации nginx...$(NC)"
	@if docker-compose -f $(COMPOSE_FILE) ps nginx | grep -q "Up"; then \
		docker-compose -f $(COMPOSE_FILE) exec nginx nginx -t && \
		docker-compose -f $(COMPOSE_FILE) exec nginx nginx -s reload && \
		echo "$(GREEN)Конфигурация nginx перезагружена!$(NC)"; \
	else \
		echo "$(RED)Контейнер nginx не запущен!$(NC)"; \
		exit 1; \
	fi

# Принудительная очистка всех кешей браузера (добавляет timestamp к статическим файлам)
.PHONY: bust-cache
bust-cache:
	@echo "$(YELLOW)Принудительная очистка кеша браузера...$(NC)"
	@TIMESTAMP=$$(date +%s); \
	echo "Cache bust timestamp: $$TIMESTAMP"; \
	docker-compose -f $(COMPOSE_FILE) exec webapp sh -c "find /app/webapp/static -name '*.css' -o -name '*.js' | head -5" || true
	@make clear-nginx-cache
	@echo "$(GREEN)Кеш браузера будет очищен при следующем обновлении!$(NC)"




#docker run -it --rm --entrypoint sh node:24-alpine
# Остановка всех сервисов
.PHONY: up-ton-dev
up-ton-dev:
	@echo "$(YELLOW)Остановка всех сервисов...$(NC)"
	docker run -it --rm -v ./ton:/ton --entrypoint sh node:24-alpine
	@echo "$(GREEN)Сервисы остановлены!$(NC)"
