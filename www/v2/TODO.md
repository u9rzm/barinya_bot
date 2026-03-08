# TODO List — Gourmet Delivery App Improvements

> **Generated:** 2026-03-06
> **Last Updated:** 2026-03-06
> **Total Tasks:** 13 P0/P1 tasks
> **Status:** ✅ ALL P0/P1 TASKS COMPLETED
> **P2 Progress:** 8/10 completed (80%)

---

## 📋 Quick Status

| Priority | Total | Completed | In Progress | Pending |
|----------|-------|-----------|-------------|---------|
| **P0 — Critical** | 5 | 5 | 0 | 0 |
| **P1 — High** | 8 | 8 | 0 | 0 |
| **P2 — Medium** | 10 | 8 | 0 | 2 |
| **TOTAL** | **23** | **21** | **0** | **2** |

---

## ✅ COMPLETED TASKS

### P0 — Critical (5/5) ✅

- [x] **P0-01:** Удалить дубликаты файлов из корня проекта
- [x] **P0-02:** Удалить серверные зависимости из production bundle
- [x] **P0-03:** Исправить .env.example
- [x] **P0-04:** Добавить валидацию пользовательского ввода
- [x] **P0-05:** Исправить TOCTOU уязвимость в проверке остатков

### P1 — High (8/8) ✅

- [x] **P1-01:** Включить строгий режим TypeScript
- [x] **P1-02:** Заменить any на интерфейсы в компонентах
- [x] **P1-03:** Добавить React Error Boundary
- [x] **P1-04:** Защитить данные в localStorage шифрованием
- [x] **P1-05:** Добавить Content Security Policy
- [x] **P1-06:** Добавить accessibility атрибуты
- [x] **P1-07:** Настроить ESLint
- [x] **P1-08:** Удалить неиспользуемые зависимости

### P2 — Medium (8/10) ✅

- [x] **P2-01:** Добавить Code Splitting ✅
- [x] **P2-02:** Создать компонент OptimizedImage ✅
- [x] **P2-03:** Добавить мемоизацию вычислений ✅
- [x] **P2-04:** Добавить дебаунс для быстрых действий ✅
- [ ] **P2-05:** Настроить Unit-тесты (Vitest)
- [ ] **P2-06:** Добавить JSDoc документацию
- [x] **P2-07:** Создать утилиту логирования ✅
- [x] **P2-08:** Вынести магические числа в константы ✅
- [x] **P2-09:** Оптимизировать поиск дубликатов в корзине ✅
- [x] **P2-10:** Добавить обработку ошибок загрузки видео ✅
- [x] **CSP Fix:** Обновить Content Security Policy ✅

---

## ✅ P2 — Medium (COMPLETED)

### [x] P2-01: Добавить Code Splitting ✅
**Completed:** 2026-03-06

**Implemented optimizations:**
1. ✅ **Dynamic import for hls.js** — 522 kB now loaded on-demand only when video is needed
2. ✅ **Lazy load CartSheet** — extracted to separate 4.5 kB chunk
3. ✅ **Lazy load ProductDetail, CheckoutSheet** — already implemented in App.tsx
4. ✅ **Optimized vite.config.ts** — better chunk splitting and minification

**Files modified:**
- `src/components/OptimizedVideo.tsx` — dynamic HLS.js import
- `src/components/MainPage.tsx` — lazy CartSheet
- `src/App.tsx` — Suspense boundaries (already present)
- `vite.config.ts` — improved build configuration

**Results:**
| Chunk | Before | After | Change |
|-------|--------|-------|--------|
| hls-vendor | 522 kB (eager) | 522 kB (lazy) | ✅ On-demand |
| MainPage | 23.51 kB | 19.54 kB | ↓ 17% |
| CartSheet | (in main) | 4.48 kB | ✅ Separated |
| Initial load | ~742 kB | ~220 kB | ✅ ↓ 70% |

**Initial bundle reduction: ~70%** (from ~742 kB to ~220 kB excluding lazy chunks)

---

### [x] P2-02: Создать компонент OptimizedImage ✅
**Completed:** 2026-03-06

**Features implemented:**
1. ✅ **Lazy loading** via Intersection Observer
2. ✅ **Placeholder options**: blur, pulse, color
3. ✅ **Error fallback** with icon
4. ✅ **Smooth fade-in** on load
5. ✅ **Replaced all `<img>`** in components

**Files created:**
- `src/components/OptimizedImage.tsx` (new)

**Files modified:**
- `src/components/CatalogSheet.tsx` — product images
- `src/components/CartSheet.tsx` — cart item images
- `src/components/ProductDetail.tsx` — addon option images
- `src/components/MainPage.tsx` — user avatar

**Expected result:** All images have placeholder and fallback ✅

---

### [x] P2-09: Оптимизировать поиск дубликатов в корзине ✅
**Completed:** 2026-03-06

**Optimization:**
- ✅ Changed from `O(n)` findIndex to `O(1)` Map lookup
- ✅ Composite key: `${product.id}:${optionsKey}`
- ✅ Cart duplicate check now constant time

**Files modified:**
- `src/App.tsx` — addToCart function

**Expected result:** O(1) lookup вместо O(n) ✅

---

### [x] P2-03: Добавить мемоизацию вычислений ✅
**Completed:** 2026-03-06

**Memoization added:**
1. ✅ **useCallback** for all event handlers:
   - `handleCategoryChange` — depends on [categories, activeCategory]
   - `recordAction` — stable empty deps
   - `handleSelectProduct` — depends on [recordAction]
   - `addToCart` — stable empty deps
   - `removeFromCart` — stable empty deps
   - `updateCartQuantity` — stable empty deps
   - `handleOrder` — depends on [recordAction]
2. ✅ **useMemo** for `isAppReady` — depends on [isLoading, categories, products]
3. ✅ **useMemo** already present in CatalogSheet for `userProfile` and `displayProducts`

**Files modified:**
- `src/App.tsx` — added useCallback and useMemo
- `src/components/CatalogSheet.tsx` — already optimized

**Expected result:** Меньше лишних ре-рендеров ✅

---

### [x] P2-04: Добавить дебаунс для быстрых действий ✅
**Completed:** 2026-03-06

**Utilities created:**
1. ✅ **debounce** — delays execution until after wait time
2. ✅ **debounceWithImmediate** — executes immediately then rate-limits
3. ✅ **throttle** — ensures max once per interval
4. ✅ **throttleWithOptions** — leading/trailing edge options

**Files created:**
- `src/utils/debounce.ts` (new)
- `src/utils/throttle.ts` (new)

**Applied to:**
- `src/components/CatalogSheet.tsx` — throttled category switching (300ms)

**Expected result:** Нет лишних вычислений при быстрых действиях ✅

---

### [x] P2-07: Создать утилиту логирования ✅
**Completed:** 2026-03-06

**Features:**
1. ✅ **Log levels**: debug, info, warn, error
2. ✅ **Auto-disable debug** in production
3. ✅ **Timestamps** and colored output
4. ✅ **Child loggers** with custom prefixes
5. ✅ **Replaced console.log** in all components

**Files created:**
- `src/utils/logger.ts` (new)

**Files modified:**
- `src/App.tsx` — replaced 8 console calls
- `src/components/OptimizedVideo.tsx` — replaced 1 console call
- `src/components/CheckoutSheet.tsx` — replaced 2 console calls

**Expected result:** В production видны только warn/error логи ✅

---

### [x] P2-08: Вынести магические числа в константы ✅
**Completed:** 2026-03-06

**Constants created:**
1. ✅ **ANIMATION** — durations, spring values
2. ✅ **DRAG** — thresholds, velocity, elastic
3. ✅ **RADIUS** — border radius values
4. ✅ **SPACING** — gap values
5. ✅ **Z_INDEX** — layer stacking
6. ✅ **TIMING** — debounce/throttle delays
7. ✅ **LOADING** — display times, timeouts
8. ✅ **Component-specific** — CATALOG, VIDEO, CART, PRODUCT
9. ✅ **THRESHOLDS** — scroll, opacity, drag

**Files created:**
- `src/constants/ui.ts` (new)

**Expected result:** Код стал читаемее, числа именованы ✅

---

### [x] P2-10: Добавить обработку ошибок загрузки видео ✅
**Completed:** 2026-03-06

**Features:**
1. ✅ **Error detection** for HLS and MP4
2. ✅ **Automatic retry** with exponential backoff (1s, 2s, 4s, 8s, max 10s)
3. ✅ **Max retries** (default: 3 attempts)
4. ✅ **Error UI** with retry button
5. ✅ **Error counter** showing attempts
6. ✅ **Manual retry** button
7. ✅ **onError callback** for parent components

**Files modified:**
- `src/components/OptimizedVideo.tsx` — added error handling

**Expected result:** Видео загружается надежно, есть fallback ✅

---

### [x] CSP Fix: Обновить Content Security Policy ✅
**Completed:** 2026-03-06

**Changes:**
1. ✅ Added `blob:` to `media-src` for HLS streams
2. ✅ Added `https://storage.sweethome38.keenetic.pro` to `connect-src`

**Files modified:**
- `index.html` — updated CSP meta tag

**Expected result:** HLS видео работают без CORS ошибок ✅

---

## 🟢 P3 — Low (1-2 месяца)

### [ ] P3-01: Добавить Service Worker
- [ ] Создать `public/sw.js`
- [ ] Настроить кэширование статики
- [ ] Добавить offline fallback страницу
- [ ] Зарегистрировать SW в `main.tsx`

**Файлы:** `public/sw.js` (новый), `src/main.tsx`  
**Ожидаемый результат:** Приложение работает offline

---

### [ ] P3-02: Интегрировать Sentry для мониторинга ошибок
- [ ] Установить `@sentry/react`
- [ ] Настроить в `main.tsx`
- [ ] Настроить sourcemaps для production
- [ ] Настроить алерты для критических ошибок

**Команды:**
```bash
npm install @sentry/react
```

**Файлы:** `src/main.tsx`, `vite.config.ts`  
**Ожидаемый результат:** Ошибки отправляются в Sentry

---

### [ ] P3-03: Написать E2E тесты (Playwright)
- [ ] Установить Playwright
- [ ] Написать тест основного flow
- [ ] Написать тест авторизации через Telegram
- [ ] Настроить запуск в CI

**Команды:**
```bash
npm install -D @playwright/test
npx playwright install
```

**Файлы:** `e2e/**/*.spec.ts` (новые)  
**Ожидаемый результат:** E2E тесты проходят в CI

---

### [ ] P3-04: Настроить CI/CD пайплайн
- [ ] Создать `.github/workflows/ci.yml`
- [ ] Добавить линт на каждый PR
- [ ] Добавить тесты на каждый PR
- [ ] Добавить build проверку
- [ ] Настроить deploy на merge в main

**Файлы:** `.github/workflows/ci.yml` (новый)  
**Ожидаемый результат:** CI запускается на каждый PR

---

### [ ] P3-05: Переиспользуемые темы через CSS variables
- [ ] Вынести цвета в CSS custom properties
- [ ] Поддержать runtime смену тем
- [ ] Упростить код переключения тем

**Файлы:** `src/index.css`, `src/App.tsx`  
**Ожидаемый результат:** Темы переключаются через CSS variables

---

### [ ] P3-06: Унифицировать язык кода
- [ ] Все идентификаторы на английском
- [ ] Пользовательские тексты вынести в i18n файлы
- [ ] Комментарии на английском

**Файлы:** Все файлы  
**Ожидаемый результат:** Консистентный стиль кода

---

### [ ] P3-07: Оптимизировать загрузку видео
- [ ] Добавить preload hints в `<head>`
- [ ] Оптимизировать poster изображения
- [ ] Настроить adaptive bitrate

**Файлы:** `index.html`, `src/components/OptimizedVideo.tsx`  
**Ожидаемый результат:** Видео загружается быстрее

---

## 📊 Progress Tracking

### Weekly Goals

#### Week 1 (P0 Critical)
- [ ] P0-01: Удалить дубликаты
- [ ] P0-02: Удалить серверные зависимости
- [ ] P0-03: Исправить .env.example
- [ ] P0-04: Валидация ввода
- [ ] P0-05: Исправить TOCTOU

#### Week 2 (P1 High — Part 1)
- [ ] P1-01: TypeScript strict mode
- [ ] P1-02: Заменить any на интерфейсы
- [ ] P1-03: Error Boundary
- [ ] P1-04: Шифрование localStorage

#### Week 3 (P1 High — Part 2)
- [ ] P1-05: CSP
- [ ] P1-06: Accessibility
- [ ] P1-07: ESLint
- [ ] P1-08: Удалить неиспользуемые зависимости

#### Week 4-5 (P2 Medium)
- [x] P2-01: Code Splitting ✅
- [x] P2-02: OptimizedImage ✅
- [x] P2-03: Мемоизация ✅
- [x] P2-04: Дебаунс ✅
- [ ] P2-05: Unit-тесты
- [ ] P2-06: JSDoc
- [x] P2-07: Логирование ✅
- [x] P2-08: Константы ✅
- [x] P2-09: Оптимизация корзины ✅
- [x] P2-10: Ошибки видео ✅
- [x] CSP Fix ✅

**P2 Progress:** 8/10 completed (80%)

#### Week 6-8 (P3 Low)
- [ ] P3-01: Service Worker
- [ ] P3-02: Sentry
- [ ] P3-03: E2E тесты
- [ ] P3-04: CI/CD
- [ ] P3-05: CSS variables
- [ ] P3-06: Унификация языка
- [ ] P3-07: Оптимизация видео

---

## 🏷️ Task Labels (для GitHub/GitLab)

```
priority:critical    — P0 задачи
priority:high        — P1 задачи
priority:medium      — P2 задачи
priority:low         — P3 задачи

type:bug             — Исправление багов
type:feature         — Новая функциональность
type:refactor        — Рефакторинг
type:security        — Безопасность
type:performance     — Производительность
type:documentation   — Документация
type:tests           — Тестирование

status:todo          — Не начато
status:in-progress   — В работе
status:review        — На ревью
status:done          — Готово
```

---

## 📝 Notes

- **Не начинать P2/P3 пока не завершены все P0**
- **P1 задачи можно выполнять параллельно**
- **Каждая задача должна иметь соответствующий PR**
- **Все изменения должны проходить code review**

---

## 🔗 Related Documents

- [Audit Report](./QWEN.md)
- [Improvements Specification](./IMPROVEMENTS_SPEC.md)
- [README](./README.md)
