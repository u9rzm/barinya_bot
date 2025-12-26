#!/bin/bash

# Тест производительности статических файлов

echo "🧪 Тестирование доступа к статическим файлам..."

# Тестируем различные типы файлов
STATIC_FILES=(
    "/static/css/light.css"
    "/static/scripts/app.js"
    "/static/scripts/menu.js"
    "/favicon.ico"
)

for file in "${STATIC_FILES[@]}"; do
    echo "📄 Тестируем: $file"
    
    # Тест через webapp напрямую
    echo -n "  Webapp (8000): "
    docker-compose -f docker-compose.yml exec webapp curl -s -o /dev/null -w "%{http_code} - %{time_total}s" http://localhost:8000$file
    echo
    
    # Тест через nginx (внутренний)
    echo -n "  Nginx (internal): "
    docker-compose -f docker-compose.yml exec nginx curl -s -o /dev/null -w "%{http_code} - %{time_total}s" http://webapp:8000$file
    echo
    
    echo
done

echo "✅ Тест завершен"
echo
echo "📊 Преимущества новой конфигурации:"
echo "  • Статические файлы /static/ - БЕЗ rate limiting"
echo "  • Кэширование 30 дней для /static/"
echo "  • Кэширование 7 дней для файлов по расширению"
echo "  • Gzip сжатие включено"
echo "  • Логирование отключено для статики"