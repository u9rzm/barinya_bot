/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useEffect, useMemo, useCallback, Suspense, lazy } from 'react';
import { AnimatePresence } from 'motion/react';
import { Product, Category, User, CartItem, AddonOption, Addon } from './constants/types';
import { cn } from './utils/cn';
import { LoadingScreen } from './components/LoadingScreen';
import { UserAction } from './services/recommendationService';
import { mediaPreloader } from './services/mediaPreloader';
import { init, swipeBehavior, viewport } from "@tma.js/sdk";
import { secureStorage } from './utils/secureStorage';
import { logger } from './utils/logger';
import { useAuth, useAuthStatus, TelegramUser, formatUserName, AuthErrorDisplay, useAuthError } from './auth';
import { UserProfileMenu } from './components/UserProfileMenu';
import { AuthDebug } from './components/AuthDebug';
import { debounce } from './utils/debounce';

// Адаптер: преобразует TelegramUser в User формат приложения
function adaptTelegramUserToAppUser(telegramUser: TelegramUser | null): User | null {
  if (!telegramUser) return null;
  return {
    id: telegramUser.id,
    username: telegramUser.username,
    name: formatUserName(telegramUser),
    avatar: telegramUser.photoUrl || '',
    // Этих полей нет в Telegram, используем значения по умолчанию или из localStorage
    preferredPaymentMethod: undefined,
    savedCards: [],
    cryptoAddress: undefined,
  };
}

// Lazy load heavy components for code splitting
const MainPage = lazy(() => import('./components/MainPage').then(m => ({ default: m.MainPage })));
const ProductDetail = lazy(() => import('./components/ProductDetail').then(m => ({ default: m.ProductDetail })));
const CheckoutSheet = lazy(() => import('./components/CheckoutSheet').then(m => ({ default: m.CheckoutSheet })));

// Главный компонент приложения: управление состоянием и навигацией
export default function App() {
  // Используем новый auth контекст
  const { auth, error, refresh, logout, clearError, isReady } = useAuth();
  const { isTelegram, isAuthenticated } = useAuthStatus();
  const { hasError, isRecoverable } = useAuthError();

  // Получаем Telegram пользователя если доступен
  const telegramUser = auth.type === 'telegram' ? auth.user : null;

  // Адаптируем TelegramUser в формат приложения
  const appUser: User | null = useMemo(
    () => adaptTelegramUserToAppUser(telegramUser),
    [telegramUser]
  );

  const [categories, setCategories] = useState<Category[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showOnboarding, setShowOnboarding] = useState(() => {
    return !localStorage.getItem('user_city');
  });
  const [_city, setCity] = useState(() => localStorage.getItem('user_city') || '');
  const [_error, setError] = useState<string | null>(null);
  const [activeCategory, setActiveCategory] = useState<string>('');
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [isCatalogOpen, setIsCatalogOpen] = useState(false);
  const [isCheckoutOpen, setIsCheckoutOpen] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);
  const [cart, setCart] = useState<CartItem[]>(() => {
    try {
      const saved = secureStorage.getItem<CartItem[]>('cart');
      if (!saved) return [];
      if (!Array.isArray(saved)) return [];
      // Sanitize items to ensure selectedOptions is always an array
      return saved.map(item => ({
        ...item,
        selectedOptions: Array.isArray(item.selectedOptions) ? item.selectedOptions : []
      }));
    } catch (e) {
      logger.error('Failed to parse cart from secureStorage', e);
      return [];
    }
  });
  const [userHistory, setUserHistory] = useState<UserAction[]>(() => {
    try {
      const saved = secureStorage.getItem<UserAction[]>('user_history');
      if (!saved) return [];
      if (!Array.isArray(saved)) return [];
      return saved;
    } catch (e) {
      logger.error('Failed to parse user_history from secureStorage', e);
      return [];
    }
  });
  // Развертывание Web App на весь экран
  useEffect(() => {
    const initializeViewport = async () => {
      try {
        init();
        // Разворачиваем приложение на весь экран и включаем поддержку свайпов
        viewport.expand();
        viewport.requestFullscreen();
        swipeBehavior.mount();
        swipeBehavior.disableVertical();
      } catch (e) {
        logger.warn('Failed to expand Web App', e);
      }
    };
    initializeViewport();
  }, []);

  // Загрузка данных из JSON
  useEffect(() => {
    const abortController = new AbortController();
    let pollingTimeout: ReturnType<typeof setTimeout> | null = null;
    
    // Debounced polling с экспоненциальной задержкой при ошибках
    const schedulePoll = (delay: number) => {
      if (pollingTimeout) clearTimeout(pollingTimeout);
      pollingTimeout = setTimeout(() => {
        fetchData(3); // Сбрасываем retries при плановом polling
      }, delay);
    };
    
    const fetchData = async (retries = 3) => {
      try {
        const res = await fetch(`./data.json?t=${Date.now()}`, {
          signal: abortController.signal
        });
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        const data = await res.json();
        const { categories, products, addonGroups, addons, options } = data;

        // Преобразуем продукты, подставляя аддоны по ID группы
        const processedProducts = products.map((p: any) => {
          let productAddons: Addon[] = p.addons || [];
          if (p.addonGroupId && addonGroups[p.addonGroupId]) {
            // Разрешаем ID аддонов в объекты из таблицы addons
            productAddons = addonGroups[p.addonGroupId]
              .map((addonId: string) => {
                const addonRaw = addons[addonId];
                if (!addonRaw) return null;

                // Разрешаем ID опций в объекты из таблицы options
                const resolvedOptions = (addonRaw.optionIds || [])
                  .map((optId: string) => options[optId])
                  .filter(Boolean);

                return {
                  ...addonRaw,
                  options: resolvedOptions
                };
              })
              .filter(Boolean);
          }
          return {
            ...p,
            addons: productAddons
          };
        });

        setCategories(categories);
        setProducts(processedProducts);
        setError(null);
        // Устанавливаем начальную категорию только при первой загрузке
        setActiveCategory(prev => {
          if (prev) return prev;
          return categories[2]?.id || categories[0]?.id || '';
        });

        setIsLoading(false);
      } catch (err) {
        // Игнорируем ошибки отмены запроса
        if (err instanceof Error && err.name === 'AbortError') {
          logger.debug('Fetch aborted');
          return;
        }
        
        logger.error('Failed to fetch data', err);
        if (retries > 0) {
          // Экспоненциальная задержка при ошибках: 2s, 4s, 8s
          const delay = (4 - retries) * 2000;
          logger.info(`Retrying fetch in ${delay}ms... (${retries} attempts left)`);
          schedulePoll(delay);
        } else {
          setError('Не удалось загрузить данные меню. Пожалуйста, проверьте интернет-соединение.');
          setIsLoading(false);
        }
      }
    };
    // Начальная загрузка
    fetchData();

    // Настройка периодического обновления с debounce (каждые 60 секунд)
    const POLLING_INTERVAL = 60000;
    schedulePoll(POLLING_INTERVAL);

    return () => {
      if (pollingTimeout) clearTimeout(pollingTimeout);
      abortController.abort(); // Отменяем все активные запросы при размонтировании
    };
  }, []);

  // Сохраняем историю в secureStorage (encrypted)
  useEffect(() => {
    secureStorage.setItem('user_history', userHistory);
  }, [userHistory]);

  // Сохраняем корзину в secureStorage (encrypted)
  useEffect(() => {
    secureStorage.setItem('cart', cart);
  }, [cart]);


  const handleCategoryChange = useCallback((direction: number) => {
    if (categories.length === 0) return;
    const currentIndex = categories.findIndex(c => c.id === activeCategory);
    let nextIndex = currentIndex + direction;
    if (nextIndex < 0) nextIndex = categories.length - 1;
    if (nextIndex >= categories.length) nextIndex = 0;
    setActiveCategory(categories[nextIndex].id);
  }, [categories, activeCategory]);

  const recordAction = useCallback((productId: string, type: 'view' | 'purchase') => {
    setUserHistory(prev => [...prev, { productId, type, timestamp: Date.now() }]);
  }, []);

  const handleSelectProduct = useCallback((product: Product) => {
    setSelectedProduct(product);
    setIsCatalogOpen(false);
    recordAction(product.id, 'view');
  }, [recordAction]);

  const addToCart = useCallback((product: Product, quantity: number = 1, options: AddonOption[] = []) => {
    setCart(prev => {
      // Optimization: Use Map for O(1) lookup instead of O(n) findIndex
      const optionsKey = options.map(o => o.id).sort().join(',');
      const compositeKey = `${product.id}:${optionsKey}`;

      // Build a map for O(1) lookup - optimized with early exit
      let existingIndex = -1;
      for (let i = 0; i < prev.length; i++) {
        const item = prev[i];
        const itemOptions = Array.isArray(item.selectedOptions) ? item.selectedOptions : [];
        const itemKey = `${item.product.id}:${itemOptions.map(o => o.id).sort().join(',')}`;
        if (itemKey === compositeKey) {
          existingIndex = i;
          break;
        }
      }

      if (existingIndex !== -1) {
        const newCart = [...prev];
        newCart[existingIndex].quantity += quantity;
        return newCart;
      }
      return [...prev, { product, quantity, selectedOptions: options }];
    });
  }, []);

  const removeFromCart = useCallback((index: number) => {
    setCart(prev => prev.filter((_, i) => i !== index));
  }, []);

  const updateCartQuantity = useCallback((index: number, quantity: number) => {
    setCart(prev => prev.map((item, i) =>
      i === index ? { ...item, quantity: Math.max(0, quantity) } : item
    ).filter(item => item.quantity > 0));
  }, []);

  const handleOrder = useCallback((product: Product) => {
    recordAction(product.id, 'purchase');
    setSelectedProduct(null);
  }, [recordAction]);

  const isAppReady = useMemo(() => !isLoading && categories.length > 0 && products.length > 0, [isLoading, categories, products]);

  // Memoized current product lookup
  const currentProduct = useMemo(() => {
    return products.find(p => p.category === activeCategory) || products[0];
  }, [products, activeCategory]);

  // Preload adjacent category products for smooth swiping
  useEffect(() => {
    if (products.length > 0 && categories.length > 0) {
      // Preload all products but with lower priority
      mediaPreloader.preloadAdjacentProducts(products);
    }
  }, [products, categories]);

  if (!isAppReady || showOnboarding) {
    return (
      <AnimatePresence>
        {(isLoading || showOnboarding) && (
          <LoadingScreen
            theme={theme}
            isAppReady={isAppReady}
            hasCity={!!localStorage.getItem('user_city')}
            products={products.slice(0, 5)} // Pass first 5 products for preloading
            onComplete={(selectedCity) => {
              setCity(selectedCity);
              setShowOnboarding(false);
            }}
          />
        )}
      </AnimatePresence>
    );
  }

  return (
    <div className={cn(
      "relative h-screen w-full overflow-hidden transition-colors duration-500",
      theme === 'dark' ? "bg-[#141414] text-white" : "bg-[#e4e3e0] text-[#141414]"
    )}>
      {/* Auth Error Display */}
      {hasError && error && (
        <AuthErrorDisplay
          error={error}
          onRetry={isRecoverable ? refresh : undefined}
          onDismiss={clearError}
          theme={theme}
        />
      )}

      <Suspense fallback={<LoadingScreen theme={theme} isAppReady={true} hasCity={true} onComplete={() => {}} />}>
        <MainPage
          activeCategory={activeCategory}
          setActiveCategory={setActiveCategory}
          currentProduct={currentProduct}
          onOpenProduct={() => handleSelectProduct(currentProduct)}
          onCategoryChange={handleCategoryChange}
          isCatalogOpen={isCatalogOpen}
          setIsCatalogOpen={setIsCatalogOpen}
          onSelectProduct={handleSelectProduct}
          telegramUser={telegramUser}
          isAuthenticated={isAuthenticated}
          theme={theme}
          setTheme={setTheme}
          isProfileMenuOpen={isProfileMenuOpen}
          setIsProfileMenuOpen={setIsProfileMenuOpen}
          categories={categories}
          products={products}
          cart={cart}
          onUpdateCartQuantity={updateCartQuantity}
          onRemoveFromCart={removeFromCart}
          onOpenCheckout={() => setIsCheckoutOpen(true)}
          isProductDetailOpen={!!selectedProduct}
        />
      </Suspense>

      {/* User Profile Menu */}
      <UserProfileMenu
        user={telegramUser}
        isLoading={!auth || auth.type === 'guest'}
        isAuthenticated={isAuthenticated}
        onLogout={logout}
        onRefresh={refresh}
        theme={theme}
        onToggleTheme={() => setTheme(prev => prev === 'light' ? 'dark' : 'light')}
        isOpen={isProfileMenuOpen}
        onClose={() => setIsProfileMenuOpen(false)}
      />

      <AnimatePresence>
        {selectedProduct && (
          <Suspense fallback={null}>
            <ProductDetail
              product={selectedProduct}
              onClose={() => setSelectedProduct(null)}
              onOrder={() => handleOrder(selectedProduct)}
              onAddToCart={(qty, opts) => addToCart(selectedProduct, qty, opts)}
              cart={cart}
            />
          </Suspense>
        )}
      </AnimatePresence>

      <Suspense fallback={null}>
        <CheckoutSheet
          isOpen={isCheckoutOpen}
          onClose={() => setIsCheckoutOpen(false)}
          cart={cart}
          onUpdateCart={setCart}
          theme={theme}
          user={appUser}
        />
      </Suspense>

      {/* Auth Debug Component (Dev only) */}
      {process.env.NODE_ENV === 'development' && <AuthDebug />}
    </div>
  );
}
