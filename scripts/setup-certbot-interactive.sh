#!/bin/bash

# Интерактивный скрипт установки Certbot и настройки копирования сертификатов
# Использование: sudo ./setup-certbot-interactive.sh

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для вывода
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка прав root
check_root() {
    if [ "$EUID" -ne 0 ]; then 
        print_error "Для запуска требуются права root. Используйте sudo!"
        exit 1
    fi
}

# Проверка зависимостей
check_dependencies() {
    print_info "Проверка зависимостей..."
    
    local missing_deps=()
    
    # Проверка наличия certbot
    if ! command -v certbot &> /dev/null; then
        missing_deps+=("certbot")
    fi
    
    # Проверка наличия cron
    if ! command -v crontab &> /dev/null; then
        missing_deps+=("cron")
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        print_warning "Отсутствуют зависимости: ${missing_deps[*]}"
        read -p "Установить автоматически? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_dependencies
        else
            print_error "Установите зависимости вручную и перезапустите скрипт"
            exit 1
        fi
    else
        print_success "Все зависимости установлены"
    fi
}

# Установка зависимостей
install_dependencies() {
    print_info "Определение дистрибутива..."
    
    if [ -f /etc/debian_version ]; then
        print_info "Обнаружен Debian/Ubuntu"
        apt-get update
        apt-get install -y certbot python3-certbot-nginx cron
        
    elif [ -f /etc/redhat-release ] || [ -f /etc/centos-release ]; then
        print_info "Обнаружен RHEL/CentOS"
        if [ -f /etc/redhat-release ]; then
            yum install -y epel-release
        fi
        yum install -y certbot python3-certbot-nginx crontabs
        
    elif [ -f /etc/arch-release ]; then
        print_info "Обнаружен Arch Linux"
        pacman -Sy --noconfirm certbot certbot-nginx cronie
        
    elif [ -f /etc/alpine-release ]; then
        print_info "Обнаружен Alpine Linux"
        apk add certbot certbot-nginx cronie
        
    else
        print_error "Дистрибутив не поддерживается автоматически"
        print_info "Установите вручную: certbot, cron"
        exit 1
    fi
}

# Получение сертификата
get_certificate() {
    print_info "=== Шаг 1: Получение SSL сертификата ==="
    
    read -p "Введите основной домен (например: example.com): " main_domain
    
    if [ -z "$main_domain" ]; then
        print_error "Домен не может быть пустым"
        exit 1
    fi
    
    additional_domains=""
    read -p "Добавить дополнительные домены? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Введите дополнительные домены через пробел (например: www.example.com mail.example.com):"
        read -a domains_array
        additional_domains="${domains_array[*]}"
    fi
    
    email=""
    read -p "Введите email для уведомлений Let's Encrypt (опционально): " email
    
    certbot_cmd="certbot certonly --standalone"
    
    if [ -n "$email" ]; then
        certbot_cmd+=" --email $email --agree-tos"
    else
        certbot_cmd+=" --register-unsafely-without-email --agree-tos"
    fi
    
    certbot_cmd+=" --non-interactive -d $main_domain"
    
    if [ -n "$additional_domains" ]; then
        for domain in ${domains_array[@]}; do
            certbot_cmd+=" -d $domain"
        done
    fi
    
    print_info "Выполняется команда: $certbot_cmd"
    
    if eval $certbot_cmd; then
        DOMAIN="$main_domain"
        ALL_DOMAINS="$main_domain $additional_domains"
        print_success "Сертификат успешно получен для: $ALL_DOMAINS"
    else
        print_error "Не удалось получить сертификат"
        exit 1
    fi
}

# Настройка резервного копирования
setup_backup() {
    print_info "=== Шаг 2: Настройка резервного копирования ==="
    
    default_backup_dir="/opt/ssl-backup/certs"
    read -p "Введите путь для резервного копирования [$default_backup_dir]: " backup_dir_input
    
    if [ -z "$backup_dir_input" ]; then
        BACKUP_DIR="$default_backup_dir"
    else
        BACKUP_DIR="$backup_dir_input"
    fi
    
    # Создание директории
    mkdir -p "$BACKUP_DIR"
    
    print_success "Резервные копии будут сохраняться в: $BACKUP_DIR"
}

# Создание скрипта копирования
create_copy_script() {
    print_info "=== Шаг 3: Создание скрипта копирования ==="
    
    SCRIPT_DIR="/usr/local/bin"
    mkdir -p "$SCRIPT_DIR"
    
    cat > "$SCRIPT_DIR/copy-certbot-certs.sh" << 'EOF'
#!/bin/bash

# Скрипт для копирования обновленных сертификатов Certbot

set -e

# Конфигурация
CONFIG_FILE="/etc/certbot-backup.conf"

# Загрузка конфигурации
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
else
    echo "Конфигурационный файл не найден: $CONFIG_FILE"
    exit 1
fi

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${LOG_DIR}/cert-copy.log"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Если домены переданы через переменную окружения (из хука Certbot)
if [ -n "$RENEWED_DOMAINS" ]; then
    domains_to_process="$RENEWED_DOMAINS"
else
    # Если домены переданы как аргумент
    if [ -n "$1" ]; then
        domains_to_process="$1"
    else
        # Используем домены из конфигурации
        domains_to_process="$DOMAINS"
    fi
fi

# Проверка наличия доменов
if [ -z "$domains_to_process" ]; then
    log_message "Ошибка: не указаны домены для обработки"
    exit 1
fi

log_message "Начало копирования сертификатов"

# Обработка каждого домена
for domain in $domains_to_process; do
    CERTBOT_DIR="/etc/letsencrypt/live/$domain"
    
    # Проверка существования директории с сертификатами
    if [ ! -d "$CERTBOT_DIR" ]; then
        log_message "Предупреждение: директория не найдена: $CERTBOT_DIR"
        continue
    fi
    
    # Создание директории для домена
    DOMAIN_BACKUP_DIR="${BACKUP_DIR}/${domain}"
    mkdir -p "$DOMAIN_BACKUP_DIR"
    
    log_message "Копирование сертификатов для: $domain"
    
    # Копирование основных файлов сертификатов
    declare -a cert_files=("fullchain.pem" "privkey.pem" "cert.pem" "chain.pem")
    
    for file in "${cert_files[@]}"; do
        if [ -f "$CERTBOT_DIR/$file" ]; then
            # Копируем основной файл
            cp "$CERTBOT_DIR/$file" "$DOMAIN_BACKUP_DIR/$file"
            
            # Создаем версию с временной меткой
            cp "$CERTBOT_DIR/$file" "$DOMAIN_BACKUP_DIR/${file%.*}_$TIMESTAMP.${file##*.}"
            
            log_message "  Скопирован: $file"
        fi
    done
    
    # Создание объединенного файла (для некоторых сервисов)
    if [ -f "$CERTBOT_DIR/fullchain.pem" ] && [ -f "$CERTBOT_DIR/privkey.pem" ]; then
        cat "$CERTBOT_DIR/fullchain.pem" "$CERTBOT_DIR/privkey.pem" > \
            "$DOMAIN_BACKUP_DIR/combined_$TIMESTAMP.pem"
        log_message "  Создан объединенный файл: combined_$TIMESTAMP.pem"
    fi
    
    # Настройка прав доступа
    chmod 600 "$DOMAIN_BACKUP_DIR/privkey.pem" 2>/dev/null || true
    chmod 644 "$DOMAIN_BACKUP_DIR/"*.pem 2>/dev/null || true
    
    # Обновление симлинков на последнюю версию
    ln -sf "$DOMAIN_BACKUP_DIR/fullchain.pem" "$DOMAIN_BACKUP_DIR/latest_fullchain.pem"
    ln -sf "$DOMAIN_BACKUP_DIR/privkey.pem" "$DOMAIN_BACKUP_DIR/latest_privkey.pem"
    
    # Сохраняем информацию о последнем копировании
    echo "$TIMESTAMP" > "$DOMAIN_BACKUP_DIR/last_backup.txt"
    
    log_message "  Копирование завершено для: $domain"
    
    # Если указан скрипт для выполнения после копирования
    if [ -n "$POST_COPY_SCRIPT" ] && [ -f "$POST_COPY_SCRIPT" ]; then
        log_message "  Выполнение пост-обработки: $POST_COPY_SCRIPT"
        source "$POST_COPY_SCRIPT" "$domain" "$DOMAIN_BACKUP_DIR"
    fi
done

log_message "Копирование сертификатов завершено"
exit 0
EOF
    
    chmod +x "$SCRIPT_DIR/copy-certbot-certs.sh"
    
    print_success "Скрипт копирования создан: $SCRIPT_DIR/copy-certbot-certs.sh"
}

# Создание конфигурационного файла
create_config_file() {
    print_info "=== Шаг 4: Создание конфигурационного файла ==="
    
    LOG_DIR="/var/log/certbot"
    mkdir -p "$LOG_DIR"
    
    cat > "/etc/certbot-backup.conf" << EOF
#!/bin/bash
# Конфигурационный файл для резервного копирования сертификатов

# Основной домен
MAIN_DOMAIN="$DOMAIN"

# Все домены через пробел
DOMAINS="$ALL_DOMAINS"

# Директория для резервного копирования
BACKUP_DIR="$BACKUP_DIR"

# Директория для логов
LOG_DIR="$LOG_DIR"

# Скрипт для выполнения после копирования (опционально)
# POST_COPY_SCRIPT="/path/to/post-copy-script.sh"

# Дополнительные настройки
MAX_BACKUPS=30  # Максимальное количество резервных копий
EOF
    
    chmod 644 "/etc/certbot-backup.conf"
    
    print_success "Конфигурационный файл создан: /etc/certbot-backup.conf"
}

# Настройка хуков Certbot
setup_certbot_hooks() {
    print_info "=== Шаг 5: Настройка хуков Certbot ==="
    
    HOOK_DIR="/etc/letsencrypt/renewal-hooks/deploy"
    mkdir -p "$HOOK_DIR"
    
    cat > "$HOOK_DIR/001-backup-certs.sh" << EOF
#!/bin/bash
# Хук для автоматического копирования сертификатов после обновления

CONFIG_FILE="/etc/certbot-backup.conf"

if [ -f "\$CONFIG_FILE" ]; then
    source "\$CONFIG_FILE"
    
    # Вызываем скрипт копирования для обновленных доменов
    if [ -n "\$RENEWED_DOMAINS" ]; then
        /usr/local/bin/copy-certbot-certs.sh "\$RENEWED_DOMAINS"
        
        # Логируем событие
        echo "\$(date): Автоматически скопированы сертификаты для: \$RENEWED_DOMAINS" >> "\$LOG_DIR/renewal-hook.log"
        
        # Пример: перезагрузка nginx
        # if command -v nginx &> /dev/null; then
        #     nginx -t && systemctl reload nginx
        #     echo "\$(date): Nginx перезагружен" >> "\$LOG_DIR/renewal-hook.log"
        # fi
    fi
fi

exit 0
EOF
    
    chmod +x "$HOOK_DIR/001-backup-certs.sh"
    
    print_success "Хук Certbot настроен: $HOOK_DIR/001-backup-certs.sh"
}

# Настройка Cron
setup_cron() {
    print_info "=== Шаг 6: Настройка планировщика Cron ==="
    
    print_info "Выберите частоту автоматического копирования:"
    echo "  1) Ежедневно в 3:00 (рекомендуется)"
    echo "  2) Еженедельно в воскресенье в 3:00"
    echo "  3) Ежемесячно 1-го числа в 3:00"
    echo "  4) Каждые 6 часов"
    echo "  5) Не настраивать cron"
    
    read -p "Ваш выбор [1-5]: " cron_choice
    
    case $cron_choice in
        1)
            cron_time="0 3 * * *"
            ;;
        2)
            cron_time="0 3 * * 0"
            ;;
        3)
            cron_time="0 3 1 * *"
            ;;
        4)
            cron_time="0 */6 * * *"
            ;;
        5)
            print_info "Cron не будет настроен"
            return
            ;;
        *)
            cron_time="0 3 * * *"
            print_info "Используется значение по умолчанию: ежедневно в 3:00"
            ;;
    esac
    
    CRON_JOB="$cron_time /usr/local/bin/copy-certbot-certs.sh >> $LOG_DIR/cron-copy.log 2>&1"
    
    # Добавляем задание в cron
    (crontab -l 2>/dev/null | grep -v "copy-certbot-certs.sh"; echo "$CRON_JOB") | crontab -
    
    print_success "Cron задание добавлено: $CRON_JOB"
}

# Настройка очистки старых резервных копий
setup_cleanup() {
    print_info "=== Шаг 7: Настройка очистки старых резервных копий ==="
    
    read -p "Настроить автоматическую очистку старых резервных копий? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cat > "/usr/local/bin/cleanup-old-certs.sh" << 'EOF'
#!/bin/bash
# Скрипт для очистки старых резервных копий сертификатов

CONFIG_FILE="/etc/certbot-backup.conf"
source "$CONFIG_FILE"

LOG_FILE="${LOG_DIR}/cleanup.log"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log_message "Начало очистки старых резервных копий"

for domain in $DOMAINS; do
    DOMAIN_BACKUP_DIR="${BACKUP_DIR}/${domain}"
    
    if [ ! -d "$DOMAIN_BACKUP_DIR" ]; then
        continue
    fi
    
    # Удаляем старые версии с временными метками, оставляя только последние MAX_BACKUPS
    cd "$DOMAIN_BACKUP_DIR"
    
    # Считаем файлы с временными метками
    backup_files=$(ls -1 | grep -E '.*_[0-9]{8}_[0-9]{6}\.pem$' | sort -r)
    count=$(echo "$backup_files" | wc -l)
    
    if [ $count -gt $MAX_BACKUPS ]; then
        files_to_delete=$(echo "$backup_files" | tail -n +$(($MAX_BACKUPS + 1)))
        for file in $files_to_delete; do
            rm -f "$file"
            log_message "Удален старый бэкап: $DOMAIN_BACKUP_DIR/$file"
        done
    fi
    
    log_message "Обработан домен: $domain (оставлено файлов: $((count > MAX_BACKUPS ? MAX_BACKUPS : count)))"
done

log_message "Очистка завершена"
EOF
        
        chmod +x "/usr/local/bin/cleanup-old-certs.sh"
        
        # Добавляем в cron (раз в неделю)
        CLEANUP_CRON="0 4 * * 0 /usr/local/bin/cleanup-old-certs.sh >> $LOG_DIR/cleanup.log 2>&1"
        (crontab -l 2>/dev/null | grep -v "cleanup-old-certs.sh"; echo "$CLEANUP_CRON") | crontab -
        
        print_success "Скрипт очистки создан и добавлен в cron"
    fi
}

# Первоначальное копирование
initial_backup() {
    print_info "=== Шаг 8: Первоначальное резервное копирование ==="
    
    /usr/local/bin/copy-certbot-certs.sh
    
    print_success "Первоначальное резервное копирование выполнено"
}

# Тестовый запуск
test_configuration() {
    print_info "=== Шаг 9: Тестирование конфигурации ==="
    
    echo "Выполняем тестовый запуск скрипта копирования..."
    
    if /usr/local/bin/copy-certbot-certs.sh; then
        print_success "Тест успешно пройден"
        
        # Показываем информацию о созданных файлах
        echo ""
        echo "Созданные резервные копии:"
        ls -la "$BACKUP_DIR/$DOMAIN/"
        echo ""
        
        # Проверяем cron
        echo "Настроенные cron задания:"
        crontab -l | grep -E "(copy-certbot|cleanup)"
        echo ""
        
        # Проверяем хуки
        echo "Настроенные хуки Certbot:"
        ls -la "/etc/letsencrypt/renewal-hooks/deploy/"
        
    else
        print_error "Тест не пройден. Проверьте логи: $LOG_DIR/cert-copy.log"
    fi
}

# Отображение итоговой информации
show_summary() {
    print_info "=== Установка завершена! ==="
    echo ""
    echo "${GREEN}Конфигурация успешно настроена:${NC}"
    echo ""
    echo "1. ${YELLOW}Сертификаты:${NC}"
    echo "   - Основной домен: $DOMAIN"
    echo "   - Все домены: $ALL_DOMAINS"
    echo "   - Расположение: /etc/letsencrypt/live/$DOMAIN/"
    echo ""
    echo "2. ${YELLOW}Резервное копирование:${NC}"
    echo "   - Директория: $BACKUP_DIR/"
    echo "   - Для каждого домена: $BACKUP_DIR/<domain>/"
    echo ""
    echo "3. ${YELLOW}Скрипты:${NC}"
    echo "   - Копирование: /usr/local/bin/copy-certbot-certs.sh"
    echo "   - Конфигурация: /etc/certbot-backup.conf"
    echo ""
    echo "4. ${YELLOW}Автоматизация:${NC}"
    echo "   - Хук Certbot: /etc/letsencrypt/renewal-hooks/deploy/001-backup-certs.sh"
    echo "   - Cron задания: 'crontab -l' для просмотра"
    echo ""
    echo "5. ${YELLOW}Логи:${NC}"
    echo "   - Основные логи: $LOG_DIR/cert-copy.log"
    echo "   - Cron логи: $LOG_DIR/cron-copy.log"
    echo "   - Логи обновления: $LOG_DIR/renewal-hook.log"
    echo ""
    echo "${GREEN}Ручные команды для управления:${NC}"
    echo "  - Ручное копирование: sudo /usr/local/bin/copy-certbot-certs.sh"
    echo "  - Принудительное обновление: sudo certbot renew --force-renewal"
    echo "  - Проверка обновления: sudo certbot renew --dry-run"
    echo "  - Просмотр cron заданий: crontab -l"
    echo "  - Просмотр логов: tail -f $LOG_DIR/cert-copy.log"
    echo ""
    echo "${YELLOW}Сертификаты будут автоматически копироваться:${NC}"
    echo "  1. При каждом обновлении через Certbot"
    echo "  2. По расписанию через cron"
    echo ""
}

# Основная функция
main() {
    clear
    echo -e "${BLUE}=======================================${NC}"
    echo -e "${BLUE}  Установка Certbot и настройка        ${NC}"
    echo -e "${BLUE}  автоматического резервного копирования ${NC}"
    echo -e "${BLUE}  SSL сертификатов                     ${NC}"
    echo -e "${BLUE}=======================================${NC}"
    echo ""
    
    # Последовательность шагов
    check_root
    check_dependencies
    get_certificate
    setup_backup
    create_copy_script
    create_config_file
    setup_certbot_hooks
    setup_cron
    setup_cleanup
    initial_backup
    test_configuration
    show_summary
    
    echo -e "${GREEN}Настройка завершена успешно!${NC}"
    echo ""
}

# Запуск основной функции
main "$@"