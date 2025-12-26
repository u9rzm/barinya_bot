#!/bin/bash

# Скрипт для ручного копирования сертификатов с параметрами
# Использование: sudo ./manual-copy-certs.sh --domain example.com --backup-dir /opt/backup

set -e

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Параметры по умолчанию
DOMAIN=""
BACKUP_DIR="/opt/ssl-backup/certs"
CONFIG_FILE="/etc/certbot-backup.conf"

# Функция вывода справки
show_help() {
    echo "Использование: $0 [ПАРАМЕТРЫ]"
    echo ""
    echo "Параметры:"
    echo "  -d, --domain DOMAIN       Домен для копирования сертификатов"
    echo "  -b, --backup-dir DIR      Директория для резервного копирования"
    echo "  -c, --config FILE         Конфигурационный файл (по умолчанию: /etc/certbot-backup.conf)"
    echo "  -a, --all                 Скопировать все домены из конфигурационного файла"
    echo "  -l, --list                Показать список доступных доменов"
    echo "  -h, --help                Показать эту справку"
    echo ""
    echo "Примеры:"
    echo "  $0 --domain example.com --backup-dir /opt/backup"
    echo "  $0 --all"
    echo "  $0 --list"
}

# Функция для показа списка доменов
list_domains() {
    if [ -f "$CONFIG_FILE" ]; then
        source "$CONFIG_FILE" 2>/dev/null || true
        echo "Домены из конфигурационного файла ($CONFIG_FILE):"
        if [ -n "$MAIN_DOMAIN" ]; then
            echo "  - Основной домен: $MAIN_DOMAIN"
        fi
        if [ -n "$DOMAINS" ]; then
            echo "  - Все домены: $DOMAINS"
        fi
        
        # Показываем директории с сертификатами
        echo ""
        echo "Существующие сертификаты в /etc/letsencrypt/live/:"
        if [ -d "/etc/letsencrypt/live" ]; then
            ls -1 "/etc/letsencrypt/live/" | while read dir; do
                if [ -f "/etc/letsencrypt/live/$dir/fullchain.pem" ]; then
                    echo "  - $dir"
                fi
            done
        fi
    else
        echo "Конфигурационный файл не найден: $CONFIG_FILE"
        echo "Доступные сертификаты в /etc/letsencrypt/live/:"
        if [ -d "/etc/letsencrypt/live" ]; then
            ls -1 "/etc/letsencrypt/live/"
        fi
    fi
}

# Разбор аргументов командной строки
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--domain)
            DOMAIN="$2"
            shift 2
            ;;
        -b|--backup-dir)
            BACKUP_DIR="$2"
            shift 2
            ;;
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -a|--all)
            COPY_ALL=true
            shift
            ;;
        -l|--list)
            list_domains
            exit 0
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Неизвестный параметр: $1"
            show_help
            exit 1
            ;;
    esac
done

# Если используется конфигурационный файл
if [ -f "$CONFIG_FILE" ] && [ -z "$DOMAIN" ] && [ -z "$COPY_ALL" ]; then
    source "$CONFIG_FILE" 2>/dev/null || true
    if [ -n "$MAIN_DOMAIN" ]; then
        DOMAIN="$MAIN_DOMAIN"
        echo -e "${YELLOW}Используется домен из конфигурации: $DOMAIN${NC}"
    fi
fi

# Проверка домена
if [ -z "$DOMAIN" ] && [ -z "$COPY_ALL" ]; then
    echo "Ошибка: не указан домен"
    echo "Используйте --domain или --all"
    show_help
    exit 1
fi

# Создание директории для бэкапов
mkdir -p "$BACKUP_DIR"

# Функция копирования для одного домена
copy_domain_certs() {
    local domain="$1"
    local backup_base="$2"
    
    CERT_DIR="/etc/letsencrypt/live/$domain"
    DOMAIN_BACKUP_DIR="$backup_base/$domain"
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    
    if [ ! -d "$CERT_DIR" ]; then
        echo "Ошибка: директория с сертификатами не найдена: $CERT_DIR"
        return 1
    fi
    
    mkdir -p "$DOMAIN_BACKUP_DIR"
    
    echo -e "${GREEN}Копирование сертификатов для: $domain${NC}"
    
    # Массив файлов для копирования
    declare -a cert_files=("fullchain.pem" "privkey.pem" "cert.pem" "chain.pem")
    
    for file in "${cert_files[@]}"; do
        if [ -f "$CERT_DIR/$file" ]; then
            # Основная копия
            cp "$CERT_DIR/$file" "$DOMAIN_BACKUP_DIR/$file"
            
            # Копия с временной меткой
            cp "$CERT_DIR/$file" "$DOMAIN_BACKUP_DIR/${file%.*}_$TIMESTAMP.pem"
            
            echo "  ✓ $file"
        fi
    done
    
    # Создание объединенного файла
    if [ -f "$CERT_DIR/fullchain.pem" ] && [ -f "$CERT_DIR/privkey.pem" ]; then
        cat "$CERT_DIR/fullchain.pem" "$CERT_DIR/privkey.pem" > \
            "$DOMAIN_BACKUP_DIR/combined_$TIMESTAMP.pem"
        echo "  ✓ Объединенный файл: combined_$TIMESTAMP.pem"
    fi
    
    # Настройка прав доступа
    chmod 600 "$DOMAIN_BACKUP_DIR/privkey.pem" 2>/dev/null || true
    chmod 644 "$DOMAIN_BACKUP_DIR/"*.pem 2>/dev/null || true
    
    # Обновление симлинков
    ln -sf "$DOMAIN_BACKUP_DIR/fullchain.pem" "$DOMAIN_BACKUP_DIR/latest_fullchain.pem"
    ln -sf "$DOMAIN_BACKUP_DIR/privkey.pem" "$DOMAIN_BACKUP_DIR/latest_privkey.pem"
    
    # Сохраняем информацию о копировании
    echo "Скопировано: $(date)" > "$DOMAIN_BACKUP_DIR/backup_info.txt"
    echo "Домен: $domain" >> "$DOMAIN_BACKUP_DIR/backup_info.txt"
    echo "Временная метка: $TIMESTAMP" >> "$DOMAIN_BACKUP_DIR/backup_info.txt"
    
    echo -e "${GREEN}  Сертификаты скопированы в: $DOMAIN_BACKUP_DIR${NC}"
    echo ""
}

# Основная логика
if [ "$COPY_ALL" = true ]; then
    # Копирование всех доменов
    if [ -f "$CONFIG_FILE" ]; then
        source "$CONFIG_FILE"
        if [ -n "$DOMAINS" ]; then
            echo "Копирование всех доменов: $DOMAINS"
            for domain in $DOMAINS; do
                copy_domain_certs "$domain" "$BACKUP_DIR"
            done
        else
            echo "В конфигурационном файле не указаны домены"
            exit 1
        fi
    else
        # Копирование всех найденных сертификатов
        echo "Копирование всех найденных сертификатов"
        if [ -d "/etc/letsencrypt/live" ]; then
            for domain_dir in /etc/letsencrypt/live/*; do
                if [ -d "$domain_dir" ] && [ -f "$domain_dir/fullchain.pem" ]; then
                    domain=$(basename "$domain_dir")
                    copy_domain_certs "$domain" "$BACKUP_DIR"
                fi
            done
        fi
    fi
else
    # Копирование одного домена
    copy_domain_certs "$DOMAIN" "$BACKUP_DIR"
fi

echo -e "${GREEN}Готово!${NC}"
echo "Резервные копии сохранены в: $BACKUP_DIR/"