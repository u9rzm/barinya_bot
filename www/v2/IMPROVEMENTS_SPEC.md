# Спецификация улучшений проекта Gourmet Delivery App

**Версия:** 1.0  
**Дата:** 2026-03-06  
**Статус:** На утверждении

---

## 1. Введение

### 1.1 Назначение документа
Данный документ описывает план улучшений для проекта Gourmet Delivery App на основе проведённого аудита. Спецификация предназначена для разработчиков, тестировщиков и менеджеров проекта.

### 1.2 Текущее состояние
- **Фреймворк:** React 19 + TypeScript + Vite 6
- **Тип приложения:** Telegram Mini App (TMA)
- **Общая оценка качества:** 2.5/5
- **Критических проблем:** 5
- **Проблем высокого приоритета:** 5
- **Проблем среднего приоритета:** 8

### 1.3 Цели улучшений
1. Устранить критические уязвимости безопасности
2. Повысить типобезопасность TypeScript
3. Оптимизировать производительность
4. Добавить тестирование
5. Улучшить accessibility

---

## 2. Приоритизация работ

### Матрица приоритетов

| Приоритет | Срок | Кол-во задач | Влияние |
|-----------|------|--------------|---------|
| **P0 — Critical** | 1-3 дня | 5 задач | Блокируют production |
| **P1 — High** | 1-2 недели | 8 задач | Высокое влияние на качество |
| **P2 — Medium** | 2-4 недели | 10 задач | Среднее влияние |
| **P3 — Low** | 1-2 месяца | 7 задач | Улучшения и оптимизации |

---

## 3. Детальная спецификация улучшений

### 3.1 P0 — Критические улучшения (Critical)

#### 3.1.1 Удаление дубликатов файлов
**Проблема:** Файлы `App.tsx` и `ProductDetail.tsx` дублируются в корне проекта

**Требования:**
- Удалить `/App.tsx` (дубликат `src/App.tsx`)
- Удалить `/ProductDetail.tsx` (дубликат `src/components/ProductDetail.tsx`)
- Проверить git status на наличие дубликатов
- Обновить `.gitignore` для предотвращения будущих дубликатов

**Критерии приёмки:**
- [ ] В корне проекта нет `.tsx` файлов
- [ ] Все импорты ссылаются на `src/` директорию
- [ ] Сборка проходит успешно

---

#### 3.1.2 Удаление серверных зависимостей из client bundle
**Проблема:** `better-sqlite3`, `express`, `dotenv` в production dependencies

**Требования:**
- Удалить из `dependencies`:
  - `better-sqlite3`
  - `express`
  - `dotenv`
- При необходимости переместить в `devDependencies`
- Проверить код на наличие импортов этих пакетов
- Запустить `npm install` и проверить сборку

**Критерии приёмки:**
- [ ] Серверные пакеты удалены из `dependencies`
- [ ] Bundle size уменьшился
- [ ] Сборка проходит без ошибок
- [ ] Приложение работает корректно

---

#### 3.1.3 Исправление .env.example
**Проблема:** Риск коммита реальных API ключей

**Требования:**
- Изменить формат плейсхолдеров
- Добавить предупреждение о безопасности
- Проверить `.gitignore` на наличие `.env*`

**Изменения:**
```bash
# Было:
GEMINI_API_KEY="MY_GEMINI_API_KEY"

# Стало:
# WARNING: Never commit real API keys to version control
GEMINI_API_KEY=<your_gemini_api_key_here>
APP_URL=<your_app_url_here>
```

**Критерии приёмки:**
- [ ] `.env.example` обновлён
- [ ] `.env*` в `.gitignore`
- [ ] Добавлен `.env` в `.gitignore` если отсутствует

---

#### 3.1.4 Валидация пользовательского ввода
**Проблема:** Отсутствие валидации в формах checkout и settings

**Требования:**
- Добавить валидацию телефона (regex для +7 формат)
- Добавить валидацию адреса (минимальная длина)
- Добавить валидацию имени
- Добавить визуальную индикацию ошибок
- Блокировать отправку при невалидных данных

**Техническая реализация:**
```typescript
// src/utils/validation.ts
export const validators = {
  phone: (value: string): boolean => /^(\+7|8)\d{10}$/.test(value.replace(/\D/g, '')),
  address: (value: string): boolean => value.trim().length >= 10,
  name: (value: string): boolean => /^[a-zA-Zа-яА-ЯёЁ\s-]{2,50}$/.test(value),
};
```

**Критерии приёмки:**
- [ ] Все поля форм имеют валидацию
- [ ] Ошибки отображаются под полями
- [ ] Кнопка отправки блокируется при ошибках
- [ ] Есть сообщения об ошибках на русском языке

---

#### 3.1.5 Исправление TOCTOU уязвимости
**Проблема:** Между проверкой остатка и заказом товар может закончиться

**Требования:**
- Добавить обработку случая "товар закончился во время оформления"
- Показать пользователю актуальный остаток
- Предложить альтернативу или возврат к каталогу

**Техническая реализация:**
```typescript
// CheckoutSheet.tsx
const handleConfirmOrder = async () => {
  // Финальная проверка перед отправкой
  const finalStockCheck = await verifyStock();
  if (!finalStockCheck.available) {
    showStockUnavailableModal(finalStockCheck);
    return;
  }
  // Отправка заказа
};
```

**Критерии приёмки:**
- [ ] Финальная проверка остатка перед заказом
- [ ] Пользователь видит актуальный статус
- [ ] Есть сценарий для "товар закончился"

---

### 3.2 P1 — Высокий приоритет (High)

#### 3.2.1 Включение строгого режима TypeScript
**Файл:** `tsconfig.json`

**Изменения:**
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "exactOptionalPropertyTypes": true
  }
}
```

**Критерии приёмки:**
- [ ] `strict: true` добавлен
- [ ] Сборка проходит без ошибок
- [ ] Все `any` заменены на конкретные типы

---

#### 3.2.2 Замена `any` на интерфейсы
**Файлы:** `App.tsx`, `MainPage.tsx`, `CatalogSheet.tsx`, `UI.tsx`

**Требования:**
- Создать интерфейсы для всех props компонентов
- Заменить `any` в callback функциях
- Типизировать события

**Пример:**
```typescript
// Было:
function MainPage({ ... }: any)

// Стало:
interface MainPageProps {
  activeCategory: string;
  setActiveCategory: (id: string) => void;
  currentProduct: Product | null;
  onOpenProduct: () => void;
  // ... остальные props
}

function MainPage({ activeCategory, ... }: MainPageProps)
```

**Критерии приёмки:**
- [ ] Нет `any` в коде компонентов
- [ ] Все props типизированы
- [ ] TypeScript компилируется без ошибок

---

#### 3.2.3 Добавление React Error Boundary
**Файл:** `src/components/ErrorBoundary.tsx` (новый)

**Требования:**
- Создать компонент класса ErrorBoundary
- Обернуть всё приложение в ErrorBoundary
- Добавить красивую страницу ошибки
- Логировать ошибки в консоль/сервис

**Техническая реализация:**
```typescript
// src/components/ErrorBoundary.tsx
export class ErrorBoundary extends Component<Props, State> {
  state = { hasError: false, error: null };
  
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }
  
  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('ErrorBoundary caught:', error, info);
  }
  
  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} />;
    }
    return this.props.children;
  }
}
```

**Критерии приёмки:**
- [ ] Компонент создан
- [ ] Приложение обёрнуто в ErrorBoundary
- [ ] Есть UI для отображения ошибки
- [ ] Кнопка "Перезагрузить" работает

---

#### 3.2.4 Защита localStorage
**Проблема:** Чувствительные данные хранятся в открытом виде

**Требования:**
- Создать утилиту шифрования для localStorage
- Шифровать cart и user_history
- Ключ шифрования хранить в env

**Техническая реализация:**
```typescript
// src/utils/secureStorage.ts
const STORAGE_KEY = import.meta.env.VITE_STORAGE_ENCRYPTION_KEY;

export const secureStorage = {
  setItem: (key: string, value: unknown) => {
    const encrypted = CryptoJS.AES.encrypt(
      JSON.stringify(value),
      STORAGE_KEY
    ).toString();
    localStorage.setItem(key, encrypted);
  },
  
  getItem: (key: string) => {
    const encrypted = localStorage.getItem(key);
    if (!encrypted) return null;
    const decrypted = CryptoJS.AES.decrypt(encrypted, STORAGE_KEY);
    return JSON.parse(decrypted.toString(CryptoJS.enc.Utf8));
  }
};
```

**Критерии приёмки:**
- [ ] Утилита создана
- [ ] cart шифруется при сохранении
- [ ] user_history шифруется при сохранении
- [ ] Данные корректно расшифровываются

---

#### 3.2.5 Content Security Policy
**Файл:** `index.html`

**Требования:**
- Добавить CSP meta-тег
- Разрешить только необходимые домены
- Включить `script-src 'self'`

**Изменения:**
```html
<!-- index.html -->
<head>
  <meta http-equiv="Content-Security-Policy" 
        content="default-src 'self'; 
                 script-src 'self' 'unsafe-inline' https://telegram.org; 
                 style-src 'self' 'unsafe-inline'; 
                 img-src 'self' data: https:; 
                 media-src 'self' https://storage.sweethome38.keenetic.pro https://assets.mixkit.co; 
                 connect-src 'self' https://api.gemini.ai;">
</head>
```

**Критерии приёмки:**
- [ ] CSP meta-тег добавлен
- [ ] Консоль не показывает CSP ошибок
- [ ] Все ресурсы загружаются корректно

---

#### 3.2.6 Accessibility атрибуты
**Файлы:** Все компоненты с интерактивными элементами

**Требования:**
- Добавить `aria-label` к кнопкам с иконками
- Добавить `role` к интерактивным элементам
- Добавить `alt` к изображениям
- Добавить `aria-expanded` для раскрывающихся элементов

**Пример:**
```typescript
// Было:
<button onClick={handleLike}>
  <Heart size={20} />
</button>

// Стало:
<button 
  onClick={handleLike}
  aria-label={isLiked ? 'Убрать из избранного' : 'Добавить в избранное'}
  aria-pressed={isLiked}
>
  <Heart size={20} aria-hidden="true" />
</button>
```

**Критерии приёмки:**
- [ ] Все кнопки имеют aria-label
- [ ] Все изображения имеют alt
- [ ] Lighthouse a11y score > 90

---

#### 3.2.7 Настройка ESLint
**Файл:** `.eslintrc.cjs` (новый), `package.json`

**Требования:**
- Установить ESLint с React плагинами
- Настроить правила для TypeScript
- Добавить pre-commit хук

**Установка:**
```bash
npm install -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin eslint-plugin-react eslint-plugin-react-hooks
```

**Критерии приёмки:**
- [ ] ESLint настроен
- [ ] `npm run lint` работает
- [ ] Нет критических ошибок линтера

---

#### 3.2.8 Удаление неиспользуемых зависимостей
**Файл:** `package.json`

**Требования:**
- Проанализировать зависимости через `depcheck`
- Удалить неиспользуемые пакеты
- Убрать дублирование vite

**Команды:**
```bash
npm install -D depcheck
npx depcheck
# Удалить найденные неиспользуемые
npm uninstall embla-carousel-react radix-ui @google/genai
```

**Критерии приёмки:**
- [ ] depcheck не находит неиспользуемых зависимостей
- [ ] Сборка работает
- [ ] Bundle size уменьшился

---

### 3.3 P2 — Средний приоритет (Medium)

#### 3.3.1 Code Splitting
**Файл:** `src/App.tsx`, `src/main.tsx`

**Требования:**
- Lazy load для тяжёлых компонентов
- Динамический импорт для модалок

**Изменения:**
```typescript
// src/App.tsx
import { lazy, Suspense } from 'react';

const ProductDetail = lazy(() => import('./components/ProductDetail'));
const CheckoutSheet = lazy(() => import('./components/CheckoutSheet'));
const CatalogSheet = lazy(() => import('./components/CatalogSheet'));

// В render:
<Suspense fallback={<LoadingSpinner />}>
  {selectedProduct && <ProductDetail ... />}
</Suspense>
```

**Критерии приёмки:**
- [ ] Компоненты загружаются лениво
- [ ] Initial bundle size уменьшился на 20%+
- [ ] Loading state отображается корректно

---

#### 3.3.2 Оптимизация изображений
**Файлы:** Все компоненты с изображениями

**Требования:**
- Добавить lazy loading
- Добавить placeholder
- Добавить fallback на ошибку
- Использовать WebP когда возможно

**Компонент:**
```typescript
// src/components/OptimizedImage.tsx (новый)
interface OptimizedImageProps {
  src: string;
  alt: string;
  className?: string;
}

export function OptimizedImage({ src, alt, className }: OptimizedImageProps) {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);
  
  return (
    <div className={cn('relative', className)}>
      {!loaded && <div className="absolute inset-0 bg-gray-200 animate-pulse" />}
      {error && <div className="absolute inset-0 bg-gray-100 flex items-center justify-center">📷</div>}
      <img
        src={src}
        alt={alt}
        loading="lazy"
        onLoad={() => setLoaded(true)}
        onError={() => setError(true)}
        className={cn('transition-opacity duration-300', loaded ? 'opacity-100' : 'opacity-0')}
      />
    </div>
  );
}
```

**Критерии приёмки:**
- [ ] Компонент создан
- [ ] Все изображения используют новый компонент
- [ ] Есть placeholder и fallback

---

#### 3.3.3 Мемоизация вычислений
**Файл:** `src/App.tsx`, `src/components/MainPage.tsx`

**Требования:**
- Добавить useMemo для expensive вычислений
- Добавить useCallback для callback функций
- Добавить React.memo для компонентов

**Изменения:**
```typescript
// App.tsx
const userProfile = useMemo(
  () => recommendationService.getUserProfile(userHistory, products),
  [userHistory, products]
);

const recommendedProducts = useMemo(
  () => recommendationService.getRecommendedProducts(products, userProfile),
  [products, userProfile]
);

const handleAddToCart = useCallback((product: Product, qty: number) => {
  // ...
}, []);
```

**Критерии приёмки:**
- [ ] useMemo добавлен к вычислениям
- [ ] useCallback добавлен к callback-ам
- [ ] React.memo добавлен к статичным компонентам

---

#### 3.3.4 Дебаунс быстрых действий
**Файл:** `src/components/CatalogSheet.tsx`, `MainPage.tsx`

**Требования:**
- Добавить дебаунс для переключения категорий
- Добавить throttle для скролла

**Утилита:**
```typescript
// src/utils/debounce.ts
export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null;
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}
```

**Критерии приёмки:**
- [ ] Утилита создана
- [ ] Применена к быстрым действиям
- [ ] Нет лишних ре-рендеров

---

#### 3.3.5 Unit-тесты
**Файлы:** `src/**/*.test.tsx` (новые)

**Требования:**
- Установить Vitest + React Testing Library
- Написать тесты для критических компонентов
- Покрытие > 60% для critical paths

**Установка:**
```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
```

**Критерии приёмки:**
- [ ] Vitest настроен
- [ ] Тесты для App.tsx
- [ ] Тесты для recommendationService
- [ ] CI запускает тесты

---

#### 3.3.6 JSDoc документация
**Файлы:** Все public API и сложные функции

**Требования:**
- Добавить JSDoc для экспортируемых функций
- Добавить @param и @returns
- Добавить @example для сложных случаев

**Пример:**
```typescript
/**
 * Добавляет товар в корзину с учётом выбранных опций
 * @param product - Товар для добавления
 * @param quantity - Количество (по умолчанию 1)
 * @param options - Выбранные опции (аддоны)
 * @returns void
 * @example
 * addToCart(latteProduct, 2, [coconutMilk, vanillaSyrup])
 */
const addToCart = (product: Product, quantity = 1, options: AddonOption[] = []) => {...};
```

**Критерии приёмки:**
- [ ] Все public функции имеют JSDoc
- [ ] IDE показывает документацию при наведении

---

#### 3.3.7 Логирование в продакшене
**Файл:** `src/utils/logger.ts` (новый)

**Требования:**
- Создать утилиту логирования
- Отключать debug логи в production
- Добавить уровни логирования

**Реализация:**
```typescript
// src/utils/logger.ts
type LogLevel = 'debug' | 'info' | 'warn' | 'error';

const LOG_LEVELS: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3
};

const currentLevel = import.meta.env.DEV ? 'debug' : 'warn';

export const logger = {
  debug: (...args: unknown[]) => LOG_LEVELS.debug >= LOG_LEVELS[currentLevel] && console.log('[DEBUG]', ...args),
  info: (...args: unknown[]) => LOG_LEVELS.info >= LOG_LEVELS[currentLevel] && console.info('[INFO]', ...args),
  warn: (...args: unknown[]) => LOG_LEVELS.warn >= LOG_LEVELS[currentLevel] && console.warn('[WARN]', ...args),
  error: (...args: unknown[]) => LOG_LEVELS.error >= LOG_LEVELS[currentLevel] && console.error('[ERROR]', ...args),
};
```

**Критерии приёмки:**
- [ ] Утилита создана
- [ ] Все console.log заменены на logger
- [ ] В production видны только warn/error

---

#### 3.3.8 Вынос магических чисел в константы
**Файлы:** `MainPage.tsx`, `CheckoutSheet.tsx`

**Требования:**
- Создать `src/constants/ui.ts`
- Вынести все магические числа
- Добавить комментарии

**Изменения:**
```typescript
// src/constants/ui.ts
export const ANIMATION_THRESHOLDS = {
  SWIPE_PERCENT: 0.15,
  SHEET_CLOSE_PX: 150,
  SHEET_TOGGLE_PX: 80,
} as const;

export const DEBOUNCE_MS = {
  CATEGORY_CHANGE: 300,
  SEARCH: 250,
} as const;

// MainPage.tsx
import { ANIMATION_THRESHOLDS } from '@/constants/ui';
const threshold = width * ANIMATION_THRESHOLDS.SWIPE_PERCENT;
```

**Критерии приёмки:**
- [ ] Константы созданы
- [ ] Магические числа заменены
- [ ] Код стал читаемее

---

### 3.4 P3 — Низкий приоритет (Low)

#### 3.4.1 Service Worker
**Файл:** `public/sw.js` (новый)

**Требования:**
- Кэширование статики
- Offline fallback страница
- Background sync для заказов

---

#### 3.4.2 Мониторинг ошибок (Sentry)
**Файл:** `src/main.tsx`

**Требования:**
- Интегрировать @sentry/react
- Настроить sourcemaps
- Настроить алерты

---

#### 3.4.3 E2E тесты
**Инструмент:** Playwright

**Требования:**
- Тест основного flow (выбор → корзина → заказ)
- Тест авторизации через Telegram
- Запуск в CI

---

#### 3.4.4 CI/CD пайплайн
**Платформа:** GitHub Actions

**Требования:**
- Линт на каждый PR
- Тесты на каждый PR
- Build проверка
- Deploy на merge в main

---

#### 3.4.5 Переиспользуемые темы через CSS variables
**Файл:** `src/index.css`

**Требования:**
- Вынести цвета в CSS custom properties
- Поддержка runtime смены тем
- Упростить код переключения тем

---

#### 3.4.6 Унификация языка кода
**Требования:**
- Все идентификаторы на английском
- Все пользовательские тексты на русском (в i18n файлах)
- Комментарии на английском

---

#### 3.4.7 Оптимизация видео
**Файл:** `src/components/OptimizedVideo.tsx`

**Требования:**
- Добавить preload hints в head
- Оптимизировать poster изображения
- Добавить adaptive bitrate настройку

---

## 4. Метрики успеха

### 4.1 Технические метрики

| Метрика | Текущее | Целевое | Приоритет |
|---------|---------|---------|-----------|
| TypeScript strict mode | ❌ | ✅ | P1 |
| `any` типы в коде | 15+ | 0 | P1 |
| Bundle size (gzipped) | ~500KB | <300KB | P2 |
| Lighthouse Performance | N/A | >90 | P2 |
| Lighthouse Accessibility | N/A | >90 | P1 |
| Test coverage | 0% | >60% | P2 |
| ESLint errors | N/A | 0 | P1 |

### 4.2 Бизнес метрики

| Метрика | Влияние |
|---------|---------|
| Время загрузки | ↓ 30% → меньше отказов |
| Конверсия в заказ | ↑ за счёт улучшения UX |
| Ошибки при заказе | ↓ за счёт валидации |
| Доступность | ↑ для пользователей с ограничениями |

---

## 5. Риски и зависимости

### 5.1 Технические риски
- **Риск:** Breaking changes при обновлении TypeScript strict mode
- **Митигация:** Постепенное включение, файл за файлом

- **Риск:** Шифрование localStorage может замедлить работу
- **Митигация:** Бенчмарки, оптимизация crypto библиотеки

### 5.2 Зависимости
- Gemini API ключ для тестирования AI функций
- Доступ к Telegram Mini App для тестирования TMA SDK
- Тестовые данные для stock.json

---

## 6. Глоссарий

| Термин | Определение |
|--------|-------------|
| TMA | Telegram Mini App |
| TOCTOU | Time Of Check To Time Of Use (уязвимость) |
| CSP | Content Security Policy |
| a11y | Accessibility (доступность) |
| bundle size | Размер итогового JS/CSS файла |

---

## 7. Приложения

### 7.1 Ссылки на документацию
- [React Error Boundaries](https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary)
- [TypeScript Strict Mode](https://www.typescriptlang.org/tsconfig/#strict)
- [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [WCAG Accessibility Guidelines](https://www.w3.org/WAI/standards-guidelines/wcag/)

### 7.2 Полезные инструменты
- `depcheck` — анализ неиспользуемых зависимостей
- `webpack-bundle-analyzer` — визуализация бандла
- `lighthouse` — аудит производительности
- `vitest` — тестирование
