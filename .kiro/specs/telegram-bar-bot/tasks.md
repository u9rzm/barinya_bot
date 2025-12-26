# Implementation Plan

- [x] 1. Настройка проекта и базовой инфраструктуры
  - Создать структуру проекта с папками: bot/, webapp/, shared/
  - Настроить Python 3.11+ виртуальное окружение
  - Установить зависимости: aiogram, FastAPI, SQLAlchemy, Alembic, Jinja2, uvicorn
  - Настроить SQLAlchemy и создать начальную схему базы данных
  - Создать .env файлы для конфигурации (TELEGRAM_BOT_TOKEN, DATABASE_URL, etc.)
  - Настроить pyproject.toml или requirements.txt
  - _Requirements: 8.1, 8.2_

- [x] 2. Создание моделей данных и миграций базы данных
  - [x] 2.1 Определить SQLAlchemy модели
    - Создать модели: User, LoyaltyLevel, PointsTransaction, Order, OrderItem, MenuItem, MenuCategory, Promotion
    - Определить связи между моделями (relationships)
    - Добавить индексы для telegram_id, referral_code, user_id
    - _Requirements: 1.2, 3.1, 3.2, 5.1, 5.2, 6.1, 6.3_
  
  - [x] 2.2 Создать начальную миграцию базы данных
    - Настроить Alembic
    - Создать миграцию для всех таблиц
    - Создать seed скрипт для начальных данных (уровни лояльности, категории меню)
    - _Requirements: 4.1, 4.2_
  
  - [x] 2.3 Написать property test для уникальности referral кодов
    - Property 20: Referral codes are unique per user
    - Validates: Requirements 5.1

- [-] 3. Реализация базовых сервисов
  - [x] 3.1 Создать UserService
    - Реализовать create_user с поддержкой referrer_id
    - Реализовать get_user_by_telegram_id
    - Реализовать update_user_status
    - Реализовать get_user_referrals
    - Реализовать set_user_level
    - _Requirements: 1.2, 1.4, 4.5, 5.2_
  
  - [ ]* 3.2 Написать property test для создания пользователя
    - **Property 1: New user registration creates database record**
    - **Validates: Requirements 1.2**
  
  - [ ]* 3.3 Написать property test для связи рефералов
    - **Property 21: Referral registration creates persistent link**
    - **Validates: Requirements 5.2, 5.6**
  
  - [x] 3.4 Создать LoyaltyService
    - Реализовать add_points с записью транзакции
    - Реализовать deduct_points с записью транзакции
    - Реализовать get_points_balance
    - Реализовать get_points_history
    - Реализовать calculate_level_for_user
    - Реализовать update_user_level с отправкой уведомления
    - Реализовать get_levels и create_level
    - _Requirements: 3.1, 3.2, 3.3, 3.5, 3.6, 3.7, 4.2, 4.3, 4.4_
  
  - [ ]* 3.5 Написать property test для начисления баллов
    - **Property 9: Order completion awards proportional points**
    - **Validates: Requirements 3.1, 3.7**
  
  - [ ]* 3.6 Написать property test для увеличения totalSpent
    - **Property 10: Order completion increases total spent**
    - **Validates: Requirements 3.2**
  
  - [ ]* 3.7 Написать property test для повышения уровня
    - **Property 11: Reaching threshold triggers level up**
    - **Validates: Requirements 3.3**
  
  - [ ]* 3.8 Написать property test для логирования транзакций
    - **Property 33: Points transactions are logged with metadata**
    - **Validates: Requirements 8.2**
  
  - [ ]* 3.9 Написать property test для расчета уровня
    - **Property 17: User level matches highest qualifying threshold**
    - **Validates: Requirements 4.4**

- [x] 4. Реализация ReferralService
  - [x] 4.1 Создать ReferralService
    - Реализовать generate_referral_code (уникальный код для пользователя)
    - Реализовать get_referral_link (формирование ссылки с ботом)
    - Реализовать register_referral с валидацией (не свой код)
    - Реализовать process_referral_reward (1% от заказа реферала)
    - Реализовать get_referral_stats
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 9.1_
  
  - [ ]* 4.2 Написать property test для награды рефереру
    - **Property 22: Referee order awards 1% to referrer**
    - **Validates: Requirements 5.3**
  
  - [ ]* 4.3 Написать property test для валидации реферальной связи
    - **Property 34: Referral rewards require valid relationship**
    - **Validates: Requirements 8.3**
  
  - [ ]* 4.4 Написать unit test для предотвращения self-referral
    - Проверить, что пользователь не может использовать свой код
    - _Requirements: 9.1_

- [x] 5. Реализация MenuService и PromotionService
  - [x] 5.1 Создать MenuService
    - Реализовать get_menu (все категории с доступными items)
    - Реализовать get_menu_item
    - Реализовать create_menu_item
    - Реализовать update_menu_item
    - Реализовать delete_menu_item (soft delete - is_available=False)
    - Реализовать get_menu_by_category
    - _Requirements: 2.1, 2.2, 2.4, 6.1, 6.2, 6.4_
  
  - [ ]* 5.2 Написать property test для фильтрации по категории
    - **Property 6: Category filtering returns only matching items**
    - **Validates: Requirements 2.2**
  
  - [ ]* 5.3 Написать property test для soft delete
    - **Property 28: Deleted menu items marked unavailable but preserved**
    - **Validates: Requirements 6.4**
  
  - [x] 5.4 Создать PromotionService
    - Реализовать create_promotion с валидацией дат
    - Реализовать get_active_promotions
    - Реализовать broadcast_promotion
    - _Requirements: 6.3, 6.5, 9.4_
  
  - [ ]* 5.5 Написать unit test для валидации дат акции
    - Проверить отклонение акции с end_date < start_date
    - _Requirements: 9.4_

- [x] 6. Реализация OrderService
  - [x] 6.1 Создать OrderService
    - Реализовать create_order с валидацией суммы
    - Реализовать get_order_by_id
    - Реализовать get_user_orders
    - Реализовать process_order_rewards (начисление баллов + реферальная награда)
    - Использовать транзакции БД для атомарности операций
    - _Requirements: 3.1, 3.2, 5.3, 7.2, 9.5_
  
  - [ ]* 6.2 Написать property test для обработки наград за заказ
    - Комбинированный тест для начисления баллов и реферальной награды
    - _Requirements: 3.1, 5.3_
  
  - [ ]* 6.3 Написать unit test для валидации суммы заказа
    - Проверить отклонение заказов с amount <= 0
    - _Requirements: 9.5_

- [x] 7. Реализация NotificationService
  - [x] 7.1 Создать NotificationService
    - Реализовать send_message с обработкой ошибок
    - Реализовать send_promotion с форматированием сообщения
    - Реализовать send_level_up_notification
    - Реализовать send_referral_reward_notification
    - Реализовать broadcast_to_active_users с логированием ошибок
    - Добавить retry логику для failed отправок
    - _Requirements: 1.1, 1.3, 3.3, 4.6, 5.4, 9.2_
  
  - [ ]* 7.2 Написать property test для broadcast только активным
    - **Property 2: Active users receive promotion broadcasts**
    - **Validates: Requirements 1.1**
  
  - [ ]* 7.3 Написать property test для содержимого акции
    - **Property 3: Promotion messages contain required information**
    - **Validates: Requirements 1.3**
  
  - [ ]* 7.4 Написать property test для продолжения broadcast при ошибках
    - **Property 36: Notification errors don't stop broadcast**
    - **Validates: Requirements 9.2**

- [x] 8. Checkpoint - Убедиться что все тесты проходят
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Реализация Telegram Bot Handler (aiogram)
  - [x] 9.1 Настроить aiogram бота с webhook
    - Создать Bot и Dispatcher
    - Настроить обработку входящих updates через webhook
    - Настроить middleware для логирования
    - _Requirements: 8.1_
  
  - [x] 9.2 Реализовать команду /start
    - Парсить referral code из параметра
    - Вызвать UserService.create_user
    - Если есть referral code, вызвать ReferralService.register_referral
    - Отправить приветственное сообщение с кнопкой Mini App
    - _Requirements: 1.2, 5.2_
  
  - [x] 9.3 Реализовать команды /menu и /profile
    - Отправить inline кнопку для открытия Mini App с соответствующим URL
    - _Requirements: 2.1_
  
  - [x] 9.4 Реализовать команду /referral
    - Вызвать ReferralService.get_referral_link
    - Отправить ссылку пользователю
    - _Requirements: 5.1_
  
  - [x] 9.5 Реализовать команду /help
    - Отправить список доступных команд с описанием
  
  - [x] 9.6 Реализовать административные команды
    - /admin_add_item - добавление позиции в меню
    - /admin_edit_item - редактирование позиции
    - /admin_create_promo - создание акции
    - /admin_broadcast - запуск рассылки
    - /admin_set_level - назначение уровня пользователю
    - Добавить проверку прав администратора (список admin telegram_id в .env)
    - _Requirements: 4.5, 4.6, 6.1, 6.2, 6.3, 6.5_
  
  - [x] 9.7 Обработать событие блокировки бота
    - Слушать ChatMemberUpdated для my_chat_member
    - Вызвать UserService.update_user_status(False) при блокировке
    - _Requirements: 1.4_
  
  - [ ]* 9.8 Написать property test для деактивации при блокировке
    - **Property 4: Blocking bot deactivates user**
    - **Validates: Requirements 1.4**

- [x] 10. Реализация REST API для Mini App (FastAPI)
  - [x] 10.1 Создать middleware для аутентификации Telegram Web App
    - Валидировать initData от Telegram Web App SDK
    - Извлекать telegram_id из валидированных данных
    - _Requirements: 8.1_
  
  - [x] 10.2 Реализовать User endpoints
    - GET /api/user/profile - вызов UserService + LoyaltyService
    - GET /api/user/stats - агрегация данных пользователя
    - _Requirements: 7.1_
  
  - [ ]* 10.3 Написать property test для профиля пользователя
    - **Property 30: Profile includes all required statistics**
    - **Validates: Requirements 7.1**
  
  - [ ]* 10.4 Написать property test для изоляции данных пользователя
    - **Property 35: User data requests return only own data**
    - **Validates: Requirements 8.4**
  
  - [x] 10.5 Реализовать Loyalty endpoints
    - GET /api/loyalty/balance
    - GET /api/loyalty/history
    - GET /api/loyalty/levels
    - _Requirements: 3.4, 3.5, 4.3_
  
  - [ ]* 10.6 Написать property test для данных профиля лояльности
    - **Property 12: Profile API returns complete loyalty data**
    - **Validates: Requirements 3.4**
  
  - [ ]* 10.7 Написать property test для истории транзакций
    - **Property 13: Points history returns all transactions**
    - **Validates: Requirements 3.5**
  
  - [x] 10.8 Реализовать Referral endpoints
    - GET /api/referral/link
    - GET /api/referral/stats
    - _Requirements: 5.1, 5.5, 7.3_
  
  - [ ]* 10.9 Написать property test для статистики рефералов
    - **Property 24: Referral stats show complete data**
    - **Validates: Requirements 5.5**
  
  - [ ]* 10.10 Написать property test для данных рефералов
    - **Property 32: Referral statistics show complete referee data**
    - **Validates: Requirements 7.3**
  
  - [x] 10.11 Реализовать Menu endpoints
    - GET /api/menu
    - GET /api/menu/categories
    - GET /api/menu/item/:id
    - _Requirements: 2.1, 2.2, 2.4_
  
  - [ ] 10.12 Написать property test для API меню
    - **Property 5: Menu API returns all categories and items**
    - **Validates: Requirements 2.1**
  
  - [ ] 10.13 Написать property test для полей menu item
    - **Property 8: Menu item response contains all required fields**
    - **Validates: Requirements 2.4**
  
  - [x] 10.14 Реализовать Order endpoints
    - POST /api/order - создание заказа с обработкой наград
    - GET /api/order/history
    - _Requirements: 3.1, 7.2_
  
  - [ ]* 10.15 Написать property test для истории заказов
    - **Property 31: Order history returns all user orders**
    - **Validates: Requirements 7.2**

- [ ] 11. Checkpoint - Убедиться что все тесты проходят
  - Ensure all tests pass, ask the user if questions arise.


- [x] 12. Создание Mini App Frontend (Jinja2 шаблоны)
  - [x] 12.1 Настроить Jinja2 шаблоны в FastAPI
    - Создать базовый layout.html с подключением Telegram Web App SDK
    - Подключить TailwindCSS через CDN
    - Настроить статические файлы (CSS, JS)
    - Инициализировать Telegram Web App SDK в JavaScript
    - _Requirements: 8.1_
  
  - [x] 12.2 Создать страницу Menu
    - Создать menu.html шаблон
    - Отобразить категории меню
    - Отобразить позиции с названием, описанием, ценой
    - Отобразить изображения если есть
    - Добавить фильтрацию по категориям через JavaScript
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  
  - [ ]* 12.3 Написать property test для отображения изображений
    - **Property 7: Menu items with images include image URLs**
    - **Validates: Requirements 2.3**
  
  - [x] 12.4 Создать страницу Profile
    - Создать profile.html шаблон
    - Отобразить баланс баллов лояльности
    - Отобразить текущий уровень лояльности
    - Отобразить прогресс до следующего уровня
    - Отобразить количество рефералов
    - Отобразить дату регистрации
    - _Requirements: 3.4, 7.1_
  
  - [x] 12.5 Создать страницу LoyaltyHistory
    - Создать loyalty_history.html шаблон
    - Отобразить список транзакций баллов
    - Показать дату, сумму и причину каждой транзакции
    - _Requirements: 3.5_
  
  - [x] 12.6 Создать страницу ReferralStats
    - Создать referral_stats.html шаблон
    - Отобразить реферальную ссылку с кнопкой копирования
    - Отобразить список приглашенных пользователей
    - Показать заработанные баллы с каждого реферала
    - _Requirements: 5.5, 7.3_
  
  - [x] 12.7 Создать страницу OrderHistory
    - Создать order_history.html шаблон
    - Отобразить список заказов с датами и суммами
    - _Requirements: 7.2_
  
  - [x] 12.8 Создать страницу LoyaltyLevels
    - Создать loyalty_levels.html шаблон
    - Отобразить все уровни лояльности
    - Показать пороги и преимущества каждого уровня
    - _Requirements: 4.3_
  
  - [x] 12.9 Настроить навигацию
    - Создать компонент навигации с вкладками: Menu, Profile, Stats
    - Настроить переходы между страницами
  
  - [x] 12.10 Применить стилизацию с TailwindCSS
    - Создать адаптивный дизайн для мобильных устройств
    - Применить Telegram theme colors через Web App SDK

- [x] 13. Обработка ошибок и логирование
  - [x] 13.1 Настроить систему логирования
    - Настроить Python logging или loguru
    - Настроить логирование ошибок, транзакций, admin действий
    - Настроить ротацию логов
    - _Requirements: 9.2_
  
  - [x] 13.2 Добавить error handling в FastAPI
    - Создать exception handlers
    - Обработка ошибок БД с retry логикой
    - Обработка ошибок валидации
    - Возврат понятных сообщений пользователю
    - _Requirements: 9.3_
  
  - [x] 13.3 Добавить обработку ошибок в Bot Handler
    - Try-except блоки для всех команд
    - Логирование всех ошибок
    - Отправка сообщений об ошибках пользователю
    - _Requirements: 9.2, 9.3_

- [x] 14. Деплой и конфигурация
  - [x] 14.1 Создать Dockerfile для приложения
    - Multi-stage build для оптимизации размера
    - Настроить production зависимости
  
  - [x] 14.2 Создать docker-compose.yml
    - Сервисы: webapp (FastAPI + bot), postgres
    - Настроить volumes для персистентности данных
    - Настроить networks
  
  - [x] 14.3 Настроить webhook для Telegram Bot
    - Зарегистрировать webhook URL в Telegram
    - Настроить SSL сертификат
  
  - [x] 14.4 Создать README с инструкциями
    - Описание проекта
    - Инструкции по установке и запуску
    - Переменные окружения
    - Команды бота

- [x] 15. Final Checkpoint - Убедиться что все тесты проходят
  - Ensure all tests pass, ask the user if questions arise.
