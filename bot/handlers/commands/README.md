# Commands Structure

Команды бота разделены на логические модули для лучшей организации кода:

## Структура модулей

### `basic.py`
- `start_command` - обработка команды /start с реферальными кодами
- `show_profile_callback` - показ профиля пользователя

### `referral.py`
- `get_referral_link_callback` - получение реферальной ссылки

### `review.py`
- `start_review_callback` - начало процесса оставления отзыва
- `cancel_review_callback` - отмена отзыва
- `handle_review_message` - обработка текста отзыва

### `admin.py`
- `upload_menu_google_sheets_callback` - загрузка меню из Google Sheets
- `settings_callback` - показ настроек администратора

### `utils.py`
- `extract_referral_code` - извлечение реферального кода из текста
- `get_main_menu_keyboard` - создание основной клавиатуры
- `admin_ids` - список ID администраторов

## Регистрация обработчиков

Все обработчики регистрируются через функции:
- `register_basic_handlers(dp)`
- `register_referral_handlers(dp)`
- `register_review_handlers(dp)`
- `register_admin_handlers(dp)`

Основная функция `register_command_handlers(dp)` в `commands.py` вызывает все эти функции.