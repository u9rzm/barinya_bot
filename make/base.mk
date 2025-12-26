
# Цвета для вывода
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color


# Проверка наличия .env файла


.PHONY: check-env
check-env:
	@if [ ! -f $(ENV_FILE) ]; then \
		echo "$(RED)Ошибка: файл $(ENV_FILE) не найден!$(NC)"; \
		echo "$(YELLOW)Скопируйте .env.example в .env и настройте переменные$(NC)"; \
		exit 1; \
	fi

# Помощь
.PHONY: help
help:
	@echo "$(GREEN)Доступные команды:$(NC)"
	@echo "  $(YELLOW)make up$(NC)              - Запустить все сервисы"
	@echo "  $(YELLOW)make down$(NC)            - Остановить все сервисы"
	@echo "  $(YELLOW)make restart$(NC)         - Перезапустить все сервисы"
	@echo "  $(YELLOW)make rebuild$(NC)         - Пересобрать и запустить приложение (с очисткой кеша)"
	@echo "  $(YELLOW)make rebuild-app$(NC)     - Пересобрать только webapp и bot (с очисткой кеша)"
	@echo "  $(YELLOW)make logs$(NC)            - Показать логи всех сервисов"
	@echo "  $(YELLOW)make logs-app$(NC)        - Показать логи webapp"
	@echo "  $(YELLOW)make logs-bot$(NC)        - Показать логи bot"
	@echo "  $(YELLOW)make logs-db$(NC)         - Показать логи базы данных"
	@echo "  $(YELLOW)make status$(NC)          - Показать статус сервисов"
	@echo "  $(YELLOW)make clean$(NC)           - Остановить и удалить контейнеры, сети"
	@echo "  $(YELLOW)make clean-all$(NC)       - Полная очистка (включая volumes)"
	@echo "  $(YELLOW)make shell-app$(NC)       - Войти в контейнер webapp"
	@echo "  $(YELLOW)make shell-bot$(NC)       - Войти в контейнер bot"
	@echo "  $(YELLOW)make shell-db$(NC)        - Войти в контейнер базы данных"
	@echo "  $(YELLOW)make db-migrate$(NC)      - Выполнить миграции базы данных"
	@echo "  $(YELLOW)make db-reset$(NC)        - Сбросить базу данных"
	@echo "  $(YELLOW)make clear-nginx-cache$(NC) - Очистить все кеши (nginx + python + статика)"
	@echo "  $(YELLOW)make clear-cache-force$(NC) - Принудительная очистка с перезапуском сервисов"
	@echo "  $(YELLOW)make reload-nginx$(NC)    - Перезагрузить конфигурацию nginx"
	@echo "  $(YELLOW)make bust-cache$(NC)      - Принудительная очистка всех кешей"
	@echo "  $(YELLOW)make test-static$(NC)     - Тестирование статических файлов"
	@echo "  $(YELLOW)make deploy$(NC)          - Быстрый деплой с очисткой кеша"
	@echo "  $(YELLOW)make deploy-frontend$(NC) - Деплой только фронтенда"
	@echo "  $(YELLOW)make dev$(NC)             - Режим разработки (rebuild + logs)"
	@echo "  $(YELLOW)make prod$(NC)            - Продакшн режим"
