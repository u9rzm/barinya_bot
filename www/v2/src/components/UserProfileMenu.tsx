import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { User, RefreshCw, Crown, Moon, Sun, CreditCard, Banknote, Gem, Check, MapPin, Home } from 'lucide-react';
import { cn } from '../utils/cn';
import { useAuth, useAuthStatus, TelegramUser, isPremiumUser, formatUserName } from '../auth';
import { secureStorage } from '../utils/secureStorage';

export type PaymentMethod = 'delivery' | 'card' | 'crypto';

interface UserProfileMenuProps {
  /**
   * @deprecated Теперь берётся из useAuth(). Не передавайте это свойство.
   */
  user?: TelegramUser | null;
  /**
   * @deprecated Теперь берётся из useAuth(). Не передавайте это свойство.
   */
  isLoading?: boolean;
  /**
   * @deprecated Теперь берётся из useAuth(). Не передавайте это свойство.
   */
  isAuthenticated?: boolean;
  onLogout?: () => void;
  onRefresh?: () => void;
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
  isOpen: boolean;
  onClose: () => void;
}

/**
 * Компонент меню профиля пользователя Telegram
 *
 * Features:
 * - Отображение аватара и имени из Telegram
 * - Индикатор Premium статуса
 * - Переключатель темы
 * - Выбор платёжного метода
 * - Редактирование адреса доставки
 * - Без кнопки выхода для Telegram пользователей
 */
export function UserProfileMenu({
  user: propUser,
  isLoading: propIsLoading,
  isAuthenticated: propIsAuthenticated,
  onLogout: propOnLogout,
  onRefresh: propOnRefresh,
  theme,
  onToggleTheme,
  isOpen,
  onClose,
}: UserProfileMenuProps) {
  const authContext = useAuth();
  const authStatus = useAuthStatus();

  const user = propUser !== undefined ? propUser : (authContext.auth.type === 'telegram' ? authContext.auth.user : null);
  const isLoading = propIsLoading !== undefined ? propIsLoading : !authContext.auth || authContext.auth.type === 'guest';
  const isAuthenticated = propIsAuthenticated !== undefined ? propIsAuthenticated : authStatus.isAuthenticated;
  const onLogout = propOnLogout || authContext.logout;
  const onRefresh = propOnRefresh || authContext.refresh;

  const [showPaymentMethods, setShowPaymentMethods] = useState(false);
  const [showAddressForm, setShowAddressForm] = useState(false);
  const [selectedPayment, setSelectedPayment] = useState<PaymentMethod>(() => {
    const saved = secureStorage.getItem<PaymentMethod>('preferred_payment');
    return saved || 'card';
  });

  // Город из localStorage
  const [city, setCity] = useState(() => localStorage.getItem('user_city') || '');
  
  // Адрес из secureStorage
  const [address, setAddress] = useState(() => {
    const saved = secureStorage.getItem<string>('user_address');
    return saved || '';
  });

  const [tempAddress, setTempAddress] = useState(address);

  // Обновляем город при изменении в localStorage
  useEffect(() => {
    const handleStorageChange = () => {
      setCity(localStorage.getItem('user_city') || '');
    };
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const handlePaymentSelect = (method: PaymentMethod) => {
    setSelectedPayment(method);
    secureStorage.setItem('preferred_payment', method);
    setShowPaymentMethods(false);
  };

  const handleSaveAddress = () => {
    if (tempAddress.trim()) {
      setAddress(tempAddress.trim());
      secureStorage.setItem('user_address', tempAddress.trim());
    }
    setShowAddressForm(false);
  };

  const handleRefresh = () => {
    onRefresh();
    // Обновляем данные из хранилища
    setCity(localStorage.getItem('user_city') || '');
    const savedAddress = secureStorage.getItem<string>('user_address');
    if (savedAddress) setAddress(savedAddress);
  };

  const paymentMethods: { id: PaymentMethod; name: string; icon: React.ReactNode }[] = [
    { id: 'delivery', name: 'При получении', icon: <Banknote size={18} /> },
    { id: 'card', name: 'Картой', icon: <CreditCard size={18} /> },
    { id: 'crypto', name: 'Криптой', icon: <Gem size={18} /> },
  ];

  const authSourceType = authContext.auth.type;

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/40 backdrop-blur-sm z-[150]"
          />

          {/* Menu */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: -20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className={cn(
              "absolute top-16 right-4 w-80 rounded-3xl overflow-hidden shadow-2xl z-[160]",
              theme === 'dark'
                ? "bg-[#1a1a1a] border border-white/10"
                : "bg-white border border-black/5"
            )}
          >
            {/* Header with Avatar */}
            <div className="relative p-6 pb-4">
              {/* Background Gradient */}
              <div className={cn(
                "absolute inset-0 opacity-10",
                theme === 'dark'
                  ? "bg-gradient-to-br from-blue-600 to-purple-600"
                  : "bg-gradient-to-br from-blue-400 to-purple-400"
              )} />

              <div className="relative flex items-start gap-4">
                {/* Avatar */}
                <div className="relative">
                  {user?.photoUrl ? (
                    <img
                      src={user.photoUrl}
                      alt={formatUserName(user)}
                      className="w-16 h-16 rounded-full object-cover border-2 border-white/20 shadow-lg"
                    />
                  ) : (
                    <div className={cn(
                      "w-16 h-16 rounded-full flex items-center justify-center border-2 shadow-lg",
                      theme === 'dark'
                        ? "bg-white/10 border-white/20"
                        : "bg-black/5 border-black/10"
                    )}>
                      <User size={32} className={cn(
                        theme === 'dark' ? "text-white/60" : "text-black/40"
                      )} />
                    </div>
                  )}

                  {/* Premium Badge */}
                  {isPremiumUser(user) && (
                    <div className="absolute -top-1 -right-1 w-6 h-6 bg-gradient-to-br from-amber-400 to-orange-500 rounded-full flex items-center justify-center shadow-lg border-2 border-white">
                      <Crown size={12} className="text-white" />
                    </div>
                  )}
                </div>

                {/* User Info */}
                <div className="flex-1 min-w-0 pt-1">
                  {isLoading ? (
                    <div className="space-y-2">
                      <div className={cn(
                        "h-5 w-32 rounded animate-pulse",
                        theme === 'dark' ? "bg-white/10" : "bg-black/10"
                      )} />
                      <div className={cn(
                        "h-3 w-20 rounded animate-pulse",
                        theme === 'dark' ? "bg-white/10" : "bg-black/10"
                      )} />
                    </div>
                  ) : isAuthenticated && user ? (
                    <>
                      <h3 className={cn(
                        "text-lg font-bold truncate",
                        theme === 'dark' ? "text-white" : "text-black"
                      )}>
                        {user.username || user.firstName || 'User'}
                      </h3>
                      <div className="flex items-center gap-2 mt-1">
                        {user.firstName && (
                          <span className={cn(
                            "text-xs",
                            theme === 'dark' ? "text-white/60" : "text-black/60"
                          )}>
                            {String(user.firstName)}
                          </span>
                        )}
                        {isPremiumUser(user) && (
                          <span className="text-[10px] px-2 py-0.5 bg-gradient-to-r from-amber-400 to-orange-500 text-white font-bold rounded-full">
                            PREMIUM
                          </span>
                        )}
                      </div>
                      {/* Source indicator */}
                      <div className="flex items-center gap-1 mt-1">
                        {authSourceType === 'telegram' && (
                          <span className="text-[10px] px-2 py-0.5 bg-blue-500/20 text-blue-400 font-medium rounded-full">
                            Telegram
                          </span>
                        )}
                        {authSourceType === 'external' && (
                          <span className="text-[10px] px-2 py-0.5 bg-green-500/20 text-green-400 font-medium rounded-full">
                            External
                          </span>
                        )}
                      </div>
                    </>
                  ) : (
                    <p className={cn(
                      "text-sm",
                      theme === 'dark' ? "text-white/60" : "text-black/60"
                    )}>
                      Гость
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Divider */}
            <div className={cn(
              "h-px mx-6",
              theme === 'dark' ? "bg-white/10" : "bg-black/5"
            )} />

            {/* Actions */}
            <div className="p-4 space-y-2">
              {/* Theme Toggle */}
              <button
                onClick={onToggleTheme}
                className={cn(
                  "w-full flex items-center gap-3 p-3 rounded-2xl transition-all active:scale-[0.98]",
                  theme === 'dark'
                    ? "bg-white/5 hover:bg-white/10"
                    : "bg-black/5 hover:bg-black/10"
                )}
              >
                <div className={cn(
                  "w-10 h-10 rounded-xl flex items-center justify-center",
                  theme === 'dark' ? "bg-white/10" : "bg-white shadow-sm"
                )}>
                  {theme === 'dark' ? (
                    <Sun size={20} className="text-white" />
                  ) : (
                    <Moon size={20} className="text-black" />
                  )}
                </div>
                <span className={cn(
                  "font-medium text-sm",
                  theme === 'dark' ? "text-white" : "text-black"
                )}>
                  {theme === 'dark' ? 'Светлая тема' : 'Тёмная тема'}
                </span>
              </button>

              {/* City Display */}
              {isAuthenticated && city && (
                <div className={cn(
                  "w-full flex items-center gap-3 p-3 rounded-2xl",
                  theme === 'dark' ? "bg-white/5" : "bg-black/5"
                )}>
                  <div className={cn(
                    "w-10 h-10 rounded-xl flex items-center justify-center",
                    theme === 'dark' ? "bg-white/10" : "bg-white shadow-sm"
                  )}>
                    <MapPin size={20} className="text-red-500" />
                  </div>
                  <div className="flex-1">
                    <span className={cn(
                      "font-medium text-sm block",
                      theme === 'dark' ? "text-white" : "text-black"
                    )}>
                      Город
                    </span>
                    <span className={cn(
                      "text-xs",
                      theme === 'dark' ? "text-white/50" : "text-black/50"
                    )}>
                      {city}
                    </span>
                  </div>
                </div>
              )}

              {/* Address Form */}
              {isAuthenticated && (
                <>
                  <button
                    onClick={() => setShowAddressForm(!showAddressForm)}
                    className={cn(
                      "w-full flex items-center gap-3 p-3 rounded-2xl transition-all active:scale-[0.98]",
                      theme === 'dark'
                        ? "bg-white/5 hover:bg-white/10"
                        : "bg-black/5 hover:bg-black/10"
                    )}
                  >
                    <div className={cn(
                      "w-10 h-10 rounded-xl flex items-center justify-center",
                      theme === 'dark' ? "bg-white/10" : "bg-white shadow-sm"
                    )}>
                      <Home size={20} className={cn(
                        address ? "text-green-500" : "text-gray-500"
                      )} />
                    </div>
                    <div className="flex-1 text-left">
                      <span className={cn(
                        "font-medium text-sm block",
                        theme === 'dark' ? "text-white" : "text-black"
                      )}>
                        Адрес доставки
                      </span>
                      <span className={cn(
                        "text-xs block truncate",
                        theme === 'dark' ? "text-white/50" : "text-black/50"
                      )}>
                        {address || 'Не указан'}
                      </span>
                    </div>
                    <Check size={16} className={cn(
                      theme === 'dark' ? "text-white/40" : "text-black/40",
                      address && "text-green-500"
                    )} />
                  </button>

                  {/* Address Input Form */}
                  <AnimatePresence>
                    {showAddressForm && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="overflow-hidden"
                      >
                        <div className={cn(
                          "p-3 rounded-2xl",
                          theme === 'dark' ? "bg-white/5" : "bg-black/5"
                        )}>
                          <label className={cn(
                            "text-xs font-medium block mb-2",
                            theme === 'dark' ? "text-white/70" : "text-black/70"
                          )}>
                            Улица, дом, квартира
                          </label>
                          <input
                            type="text"
                            value={tempAddress}
                            onChange={(e) => setTempAddress(e.target.value)}
                            placeholder="ул. Пушкина, д. 10, кв. 5"
                            className={cn(
                              "w-full px-3 py-2 rounded-xl text-sm mb-3 outline-none transition-all",
                              theme === 'dark'
                                ? "bg-white/10 text-white placeholder-white/30 focus:bg-white/20"
                                : "bg-white border border-black/10 text-black placeholder-black/30 focus:border-black/30"
                            )}
                          />
                          <div className="flex gap-2">
                            <button
                              onClick={handleSaveAddress}
                              disabled={!tempAddress.trim()}
                              className={cn(
                                "flex-1 py-2 rounded-xl text-sm font-medium transition-all",
                                tempAddress.trim()
                                  ? "bg-blue-500 text-white hover:bg-blue-600"
                                  : theme === 'dark'
                                    ? "bg-white/5 text-white/30"
                                    : "bg-black/5 text-black/30"
                              )}
                            >
                              Сохранить
                            </button>
                            <button
                              onClick={() => {
                                setTempAddress(address);
                                setShowAddressForm(false);
                              }}
                              className={cn(
                                "flex-1 py-2 rounded-xl text-sm font-medium transition-all",
                                theme === 'dark'
                                  ? "bg-white/5 text-white hover:bg-white/10"
                                  : "bg-black/5 text-black hover:bg-black/10"
                              )}
                            >
                              Отмена
                            </button>
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>

                  {/* Payment Method Button */}
                  <button
                    onClick={() => setShowPaymentMethods(!showPaymentMethods)}
                    className={cn(
                      "w-full flex items-center gap-3 p-3 rounded-2xl transition-all active:scale-[0.98]",
                      theme === 'dark'
                        ? "bg-white/5 hover:bg-white/10"
                        : "bg-black/5 hover:bg-black/10"
                    )}
                  >
                    <div className={cn(
                      "w-10 h-10 rounded-xl flex items-center justify-center",
                      theme === 'dark' ? "bg-white/10" : "bg-white shadow-sm"
                    )}>
                      {selectedPayment === 'delivery' && <Banknote size={20} className="text-green-500" />}
                      {selectedPayment === 'card' && <CreditCard size={20} className="text-blue-500" />}
                      {selectedPayment === 'crypto' && <Gem size={20} className="text-purple-500" />}
                    </div>
                    <div className="flex-1 text-left">
                      <span className={cn(
                        "font-medium text-sm block",
                        theme === 'dark' ? "text-white" : "text-black"
                      )}>
                        Способ оплаты
                      </span>
                      <span className={cn(
                        "text-xs block",
                        theme === 'dark' ? "text-white/50" : "text-black/50"
                      )}>
                        {paymentMethods.find(m => m.id === selectedPayment)?.name}
                      </span>
                    </div>
                    <Check size={16} className={cn(
                      theme === 'dark' ? "text-white/40" : "text-black/40"
                    )} />
                  </button>

                  {/* Payment Methods Dropdown */}
                  <AnimatePresence>
                    {showPaymentMethods && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="overflow-hidden"
                      >
                        <div className={cn(
                          "p-2 rounded-2xl",
                          theme === 'dark' ? "bg-white/5" : "bg-black/5"
                        )}>
                          {paymentMethods.map((method) => (
                            <button
                              key={method.id}
                              onClick={() => handlePaymentSelect(method.id)}
                              className={cn(
                                "w-full flex items-center gap-3 p-3 rounded-xl transition-all active:scale-[0.98]",
                                selectedPayment === method.id
                                  ? theme === 'dark'
                                    ? "bg-white/10"
                                    : "bg-white shadow-sm"
                                  : theme === 'dark'
                                    ? "hover:bg-white/5"
                                    : "hover:bg-black/5"
                              )}
                            >
                              <div className={cn(
                                "w-8 h-8 rounded-lg flex items-center justify-center",
                                selectedPayment === method.id
                                  ? theme === 'dark'
                                    ? "bg-white/20"
                                    : "bg-white shadow"
                                  : theme === 'dark'
                                    ? "bg-white/5"
                                    : "bg-black/5"
                              )}>
                                {method.icon}
                              </div>
                              <span className={cn(
                                "font-medium text-sm flex-1 text-left",
                                theme === 'dark' ? "text-white" : "text-black"
                              )}>
                                {method.name}
                              </span>
                              {selectedPayment === method.id && (
                                <Check size={16} className={cn(
                                  theme === 'dark' ? "text-white" : "text-black"
                                )} />
                              )}
                            </button>
                          ))}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>

                  {/* Restore/Refresh Button */}
                  <button
                    onClick={handleRefresh}
                    disabled={isLoading}
                    className={cn(
                      "w-full flex items-center gap-3 p-3 rounded-2xl transition-all active:scale-[0.98]",
                      theme === 'dark'
                        ? "bg-white/5 hover:bg-white/10"
                        : "bg-black/5 hover:bg-black/10",
                      isLoading && "opacity-50 cursor-not-allowed"
                    )}
                  >
                    <div className={cn(
                      "w-10 h-10 rounded-xl flex items-center justify-center",
                      theme === 'dark' ? "bg-white/10" : "bg-white shadow-sm"
                    )}>
                      <RefreshCw size={20} className={cn(
                        "text-blue-500",
                        isLoading && "animate-spin"
                      )} />
                    </div>
                    <div className="flex-1">
                      <span className={cn(
                        "font-medium text-sm block",
                        theme === 'dark' ? "text-white" : "text-black"
                      )}>
                        Восстановить профиль
                      </span>
                      <span className={cn(
                        "text-xs block",
                        theme === 'dark' ? "text-white/50" : "text-black/50"
                      )}>
                        Если данные потерялись
                      </span>
                    </div>
                  </button>
                </>
              )}
            </div>

            {/* Footer */}
            <div className={cn(
              "p-4 pt-0 text-center text-xs",
              theme === 'dark' ? "text-white/40" : "text-black/40"
            )}>
              {isAuthenticated && user ? (
                <p>ID: {user.id}</p>
              ) : (
                <p>Войдите через Telegram</p>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
