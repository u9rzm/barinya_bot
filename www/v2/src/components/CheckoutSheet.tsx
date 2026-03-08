import { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, CheckCircle2, AlertCircle, Loader2, ArrowRight } from 'lucide-react';
import { CartItem, Product, User } from '../constants/types';
import { cn } from '../utils/cn';
import { validators, validationMessages } from '../utils/validation';
import { logger } from '../utils/logger';
import { debounce } from '../utils/debounce';

interface CheckoutSheetProps {
  isOpen: boolean;
  onClose: () => void;
  cart: CartItem[];
  onUpdateCart: (newCart: CartItem[]) => void;
  theme: 'light' | 'dark';
  user: User | null;
}

interface StockItem {
  id: string;
  weight: string;
  price: number;
}

export function CheckoutSheet({ isOpen, onClose, cart, onUpdateCart, theme, user }: CheckoutSheetProps) {
  const [status, setStatus] = useState<'verifying' | 'ready' | 'error' | 'success' | 'shortage'>('verifying');
  const [stockOptions, setStockOptions] = useState<Record<string, StockItem[]>>({});
  const [selectedStockItems, setSelectedStockItems] = useState<Record<number, StockItem>>({});
  const [paymentMethod, setPaymentMethod] = useState<'delivery' | 'card' | 'crypto'>(user?.preferredPaymentMethod || 'card');
  const [shortageItems, setShortageItems] = useState<{ name: string; id: string; requested: number; available: number }[]>([]);
  
  // User delivery information with validation
  const [customerName, setCustomerName] = useState(user?.name || '');
  const [customerPhone, setCustomerPhone] = useState('');
  const [customerAddress, setCustomerAddress] = useState('');
  const [formErrors, setFormErrors] = useState<{
    name?: string | null;
    phone?: string | null;
    address?: string | null;
  }>({});
  const [isFormValid, setIsFormValid] = useState(false);
  
  // AbortController для отмены fetch запросов
  const abortControllerRef = useRef<AbortController | null>(null);

  // Мемоизируем flatItems для избежания лишних вычислений
  const flatItems = useMemo(() => 
    cart.flatMap(item =>
      Array(item.quantity).fill(null).map(() => ({
        ...item,
        quantity: 1
      }))
    ),
    [cart]
  );

  // Update payment method if user preference changes or when sheet opens
  useEffect(() => {
    if (isOpen && user?.preferredPaymentMethod) {
      setPaymentMethod(user.preferredPaymentMethod);
    }
  }, [isOpen, user?.preferredPaymentMethod]);

  // Validate form fields with debounce
  const validateForm = useCallback(() => {
    const errors = {
      name: validators.name(customerName) ? null : validationMessages.name,
      phone: validators.phone(customerPhone) ? null : validationMessages.phone,
      address: validators.address(customerAddress) ? null : validationMessages.address,
    };

    // Don't show errors until user has typed something
    if (!customerName) errors.name = null;
    if (!customerPhone) errors.phone = null;
    if (!customerAddress) errors.address = null;

    setFormErrors(errors);

    const isValid = validators.name(customerName) &&
                    validators.phone(customerPhone) &&
                    validators.address(customerAddress);
    setIsFormValid(isValid);
  }, [customerName, customerPhone, customerAddress]);

  // Debounced validation - updates 300ms after user stops typing
  const debouncedValidate = useMemo(() => 
    debounce(validateForm, 300),
    [validateForm]
  );

  useEffect(() => {
    debouncedValidate();
  }, [customerName, customerPhone, customerAddress, debouncedValidate]);

  const paymentMethods = useMemo(() => [
    { id: 'card', name: 'Картой', icon: '💳' },
    { id: 'crypto', name: 'Криптой', icon: '💎' },
    { id: 'delivery', name: 'При получении', icon: '💵' },
  ] as const, []);

  const parseWeight = useCallback((weightStr: string) => {
    return parseFloat(weightStr.replace(/[^\d.]/g, '')) || 0;
  }, []);

  const getItemPrice = useCallback((item: any, index: number) => {
    const stockItem = selectedStockItems[index];
    const basePrice = stockItem ? stockItem.price : item.product.price;
    const options = Array.isArray(item.selectedOptions) ? item.selectedOptions : [];
    const addonsPrice = options.reduce((acc: number, opt: any) => acc + (opt.price || 0), 0);
    return basePrice + addonsPrice;
  }, [selectedStockItems]);

  useEffect(() => {
    if (isOpen && status !== 'success') {
      verifyStock();
    }
    
    // Cleanup при закрытии
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [isOpen, cart]);

  // Мемоизируем вычисление итоговой суммы
  const finalTotal = useMemo(() => 
    flatItems.reduce((acc, item, index) => acc + getItemPrice(item, index), 0),
    [flatItems, getItemPrice]
  );

  const verifyStock = async (retries = 2) => {
    // Отменяем предыдущий запрос если есть
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    // Создаём новый AbortController
    abortControllerRef.current = new AbortController();
    
    setStatus('verifying');
    try {
      const response = await fetch(`./stock.json?t=${Date.now()}`, {
        signal: abortControllerRef.current.signal
      });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      const allStock: Record<string, StockItem[]> = data.stock;

      setStockOptions(allStock);

      // Проверка на наличие достаточного количества на складе
      const shortages: typeof shortageItems = [];
      cart.forEach(item => {
        const available = (allStock[item.product.id] || []).length;
        if (item.quantity > available) {
          shortages.push({
            id: item.product.id,
            name: item.product.name,
            requested: item.quantity,
            available: available
          });
        }
      });

      if (shortages.length > 0) {
        setShortageItems(shortages);
        setStatus('shortage');
        return;
      }

      const initialSelected: Record<number, StockItem> = {};
      const usedStockIds = new Set<string>();
      
      flatItems.forEach((item, index) => {
        const options = allStock[item.product.id] || [];
        if (options.length > 0) {
          const targetWeight = parseWeight(item.product.volume);
          
          // Фильтруем уже использованные ID для этого товара
          const availableOptions = options.filter(opt => !usedStockIds.has(opt.id));
          
          if (availableOptions.length > 0) {
            // Находим ближайший вес среди доступных
            const closest = availableOptions.reduce((prev, curr) => {
              return (Math.abs(parseWeight(curr.weight) - targetWeight) < Math.abs(parseWeight(prev.weight) - targetWeight) ? curr : prev);
            });
            initialSelected[index] = closest;
            usedStockIds.add(closest.id);
          }
        }
      });

      setSelectedStockItems(initialSelected);
      setTimeout(() => setStatus('ready'), 1200);
    } catch (err) {
      logger.error('Stock verification failed', err);
      if (retries > 0) {
        setTimeout(() => verifyStock(retries - 1), 1000);
      } else {
        setStatus('error');
      }
    }
  };

  const handleAdjustCart = () => {
    const newCart = cart.map(item => {
      const shortage = shortageItems.find(s => s.id === item.product.id);
      if (shortage) {
        return { ...item, quantity: shortage.available };
      }
      return item;
    }).filter(item => item.quantity > 0);

    onUpdateCart(newCart);
    setStatus('verifying');
    setShortageItems([]);
  };

  const handleConfirmOrder = async () => {
    // Final form validation before order
    if (!isFormValid) {
      // Trigger validation display
      setFormErrors({
        name: customerName ? (validators.name(customerName) ? null : validationMessages.name) : validationMessages.required,
        phone: customerPhone ? (validators.phone(customerPhone) ? null : validationMessages.phone) : validationMessages.required,
        address: customerAddress ? (validators.address(customerAddress) ? null : validationMessages.address) : validationMessages.required,
      });
      return;
    }

    setStatus('verifying');

    try {
      // Отменяем предыдущий запрос если есть
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      abortControllerRef.current = new AbortController();
      
      // Финальная проверка перед оплатой
      const response = await fetch(`./stock.json?t=${Date.now()}`, {
        signal: abortControllerRef.current.signal
      });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      const allStock: Record<string, StockItem[]> = data.stock;

      // 1. Проверяем общее количество еще раз
      const shortages: typeof shortageItems = [];
      cart.forEach(item => {
        const available = (allStock[item.product.id] || []).length;
        if (item.quantity > available) {
          shortages.push({
            id: item.product.id,
            name: item.product.name,
            requested: item.quantity,
            available: available
          });
        }
      });

      if (shortages.length > 0) {
        setShortageItems(shortages);
        setStatus('shortage');
        return;
      }

      // 2. Проверяем, что все выбранные ID сток-айтемов все еще существуют в базе и уникальны
      const selectedIds = new Set<string>();
      let hasDuplicates = false;
      
      const invalidSelections = Object.entries(selectedStockItems).some(([idx, selected]) => {
        const index = parseInt(idx);
        const stockItem = selected as StockItem;
        
        if (selectedIds.has(stockItem.id)) {
          hasDuplicates = true;
        }
        selectedIds.add(stockItem.id);

        const productStock = allStock[flatItems[index].product.id] || [];
        return !productStock.some(opt => opt.id === stockItem.id);
      });

      if (invalidSelections || hasDuplicates) {
        // Если база обновилась, наши ID пропали или задублировались - перепроверяем всё
        verifyStock();
        return;
      }

      // 3. Проверяем, что для каждой единицы товара сделан выбор
      if (Object.keys(selectedStockItems).length !== flatItems.length) {
        verifyStock();
        return;
      }

      // Имитируем задержку транзакции
      setTimeout(() => setStatus('success'), 1500);
    } catch (err) {
      logger.error('Final stock check failed', err);
      setStatus('error');
    }
  };

  const handleSelectStockItem = (flatIndex: number, stockItem: StockItem) => {
    setSelectedStockItems(prev => ({
      ...prev,
      [flatIndex]: stockItem
    }));
  };

  // Проверяем, занят ли конкретный сток-айтем другим юнитом того же товара
  const isStockItemTaken = (stockItemId: string, currentFlatIndex: number, productId: string) => {
    return Object.entries(selectedStockItems).some(([idx, selected]) => {
      const index = parseInt(idx);
      return index !== currentFlatIndex && 
             (selected as StockItem).id === stockItemId && 
             flatItems[index].product.id === productId;
    });
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={status !== 'verifying' ? onClose : undefined}
            className="fixed inset-0 bg-black/80 backdrop-blur-md z-[200]"
          />
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className={cn(
              "fixed inset-x-0 bottom-0 z-[210] rounded-t-[40px] max-h-[90vh] flex flex-col",
              theme === 'dark' ? "bg-[#1a1a1a] text-white" : "bg-[#f5f5f0] text-black"
            )}
          >
            <div className="w-12 h-1.5 bg-black/10 rounded-full mx-auto mt-4 mb-2" />
            
            <header className="p-6 flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold">Оформление</h2>
                <p className="text-xs opacity-40">Уточнение веса и стоимости</p>
              </div>
              {status !== 'verifying' && status !== 'success' && (
                <button 
                  onClick={onClose} 
                  aria-label="Закрыть оформление"
                  className="w-10 h-10 rounded-full bg-black/5 flex items-center justify-center hover:bg-black/10 transition-colors"
                >
                  <X size={20} aria-hidden="true" />
                </button>
              )}
            </header>

            <div className="flex-1 overflow-y-auto p-6">
              {status === 'verifying' && (
                <div className="h-64 flex flex-col items-center justify-center space-y-4">
                  <Loader2 size={40} className="animate-spin text-blue-600" />
                  <p className="text-lg font-medium opacity-60">Связываемся со складом...</p>
                </div>
              )}

              {status === 'shortage' && (
                <div className="h-full flex flex-col items-center justify-center text-center space-y-6 py-12">
                  <div className="w-24 h-24 bg-amber-500/20 rounded-full flex items-center justify-center text-amber-500">
                    <AlertCircle size={60} />
                  </div>
                  <div className="space-y-2">
                    <h3 className="text-2xl font-bold">Недостаточно на складе</h3>
                    <p className="opacity-60">Некоторые товары закончились или их меньше, чем вы заказали:</p>
                  </div>
                  
                  <div className="w-full space-y-3">
                    {shortageItems.map(item => (
                      <div key={item.id} className="flex justify-between items-center p-4 bg-black/5 rounded-2xl">
                        <span className="font-medium">{item.name}</span>
                        <span className="text-sm opacity-60">
                          {item.requested} → <span className="text-amber-600 font-bold">{item.available} шт.</span>
                        </span>
                      </div>
                    ))}
                  </div>

                  <div className="w-full space-y-3 pt-4">
                    <button 
                      onClick={handleAdjustCart}
                      className="w-full py-4 bg-blue-600 text-white rounded-2xl font-bold shadow-xl shadow-blue-600/20 active:scale-95 transition-all"
                    >
                      Исправить и продолжить
                    </button>
                    <button 
                      onClick={onClose}
                      className="w-full py-4 bg-black/5 rounded-2xl font-bold active:scale-95 transition-all"
                    >
                      Вернуться в корзину
                    </button>
                  </div>
                </div>
              )}

              {status === 'ready' && (
                <div className="space-y-8">
                  {/* Customer Information Form */}
                  <div className="space-y-4">
                    <h3 className="text-sm uppercase tracking-wider opacity-40 font-bold">Данные получателя</h3>
                    
                    <div className="space-y-4">
                      {/* Name Field */}
                      <div className="space-y-1.5">
                        <label className="text-xs opacity-60 font-medium">Имя</label>
                        <input
                          type="text"
                          value={customerName}
                          onChange={(e) => setCustomerName(e.target.value)}
                          placeholder="Иван Иванов"
                          className={cn(
                            "w-full px-4 py-3.5 rounded-2xl bg-black/5 border transition-all outline-none",
                            "focus:border-blue-500 focus:bg-black/10",
                            formErrors.name ? "border-red-500 bg-red-500/10" : "border-transparent"
                          )}
                        />
                        {formErrors.name && (
                          <p className="text-xs text-red-500 flex items-center gap-1">
                            <AlertCircle size={12} />
                            {formErrors.name}
                          </p>
                        )}
                      </div>

                      {/* Phone Field */}
                      <div className="space-y-1.5">
                        <label className="text-xs opacity-60 font-medium">Телефон</label>
                        <input
                          type="tel"
                          value={customerPhone}
                          onChange={(e) => setCustomerPhone(e.target.value)}
                          placeholder="+7 (999) 123-45-67"
                          className={cn(
                            "w-full px-4 py-3.5 rounded-2xl bg-black/5 border transition-all outline-none",
                            "focus:border-blue-500 focus:bg-black/10",
                            formErrors.phone ? "border-red-500 bg-red-500/10" : "border-transparent"
                          )}
                        />
                        {formErrors.phone && (
                          <p className="text-xs text-red-500 flex items-center gap-1">
                            <AlertCircle size={12} />
                            {formErrors.phone}
                          </p>
                        )}
                      </div>

                      {/* Address Field */}
                      <div className="space-y-1.5">
                        <label className="text-xs opacity-60 font-medium">Адрес доставки</label>
                        <input
                          type="text"
                          value={customerAddress}
                          onChange={(e) => setCustomerAddress(e.target.value)}
                          placeholder="Улица, дом, квартира"
                          className={cn(
                            "w-full px-4 py-3.5 rounded-2xl bg-black/5 border transition-all outline-none",
                            "focus:border-blue-500 focus:bg-black/10",
                            formErrors.address ? "border-red-500 bg-red-500/10" : "border-transparent"
                          )}
                        />
                        {formErrors.address && (
                          <p className="text-xs text-red-500 flex items-center gap-1">
                            <AlertCircle size={12} />
                            {formErrors.address}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="h-px bg-black/5" />

                  {/* Order Items */}
                  <div className="space-y-4">
                    <h3 className="text-sm uppercase tracking-wider opacity-40 font-bold">Товары</h3>
                    <div className="space-y-6">
                    {flatItems.map((item, i) => {
                      const options = stockOptions[item.product.id] || [];
                      const selected = selectedStockItems[i];
                      
                      return (
                        <div key={i} className="space-y-3">
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <p className="font-bold text-lg">
                                {item.product.name} 
                                {flatItems.filter(fi => fi.product.id === item.product.id).length > 1 && (
                                  <span className="text-xs opacity-40 ml-2">
                                    (№{flatItems.slice(0, i + 1).filter(fi => fi.product.id === item.product.id).length})
                                  </span>
                                )}
                              </p>
                              <p className="text-xs opacity-40">Базовый вес: {item.product.volume}</p>
                            </div>
                            <div className="text-right">
                              <p className="font-bold text-lg">{getItemPrice(item, i)} ₽</p>
                            </div>
                          </div>

                          {options.length > 1 && (
                            <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
                              {options.map((opt) => {
                                const isTaken = isStockItemTaken(opt.id, i, item.product.id);
                                return (
                                  <button
                                    key={opt.id}
                                    disabled={isTaken}
                                    onClick={() => handleSelectStockItem(i, opt)}
                                    className={cn(
                                      "px-4 py-2 rounded-xl text-xs font-medium whitespace-nowrap transition-all border",
                                      selected?.id === opt.id 
                                        ? "bg-blue-600 text-white border-blue-600 shadow-lg shadow-blue-600/20" 
                                        : isTaken 
                                          ? "bg-black/5 border-transparent opacity-20 cursor-not-allowed"
                                          : "bg-black/5 border-transparent opacity-60"
                                    )}
                                  >
                                    {opt.weight} — {opt.price} ₽
                                  </button>
                                );
                              })}
                            </div>
                          )}
                          
                          <div className="h-px bg-black/5 w-full" />
                        </div>
                      );
                    })}
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h3 className="text-sm uppercase tracking-wider opacity-40 font-bold">Способ оплаты</h3>
                    <div className="grid grid-cols-3 gap-3">
                      {paymentMethods.map((method) => (
                        <button
                          key={method.id}
                          onClick={() => setPaymentMethod(method.id)}
                          className={cn(
                            "flex flex-col items-center gap-2 p-4 rounded-2xl border transition-all active:scale-95",
                            paymentMethod === method.id
                              ? "bg-blue-600 border-blue-600 text-white shadow-lg shadow-blue-600/20"
                              : "bg-black/5 border-transparent opacity-60"
                          )}
                        >
                          <span className="text-xl">{method.icon}</span>
                          <span className="text-[10px] font-bold text-center leading-tight">{method.name}</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="p-6 bg-black/5 rounded-3xl space-y-3">
                    <div className="flex justify-between items-center opacity-60 text-sm">
                      <span>Товары ({flatItems.length})</span>
                      <span>{finalTotal} ₽</span>
                    </div>
                    <div className="flex justify-between items-center opacity-60 text-sm">
                      <span>Доставка</span>
                      <span className="text-green-500 font-bold">Бесплатно</span>
                    </div>
                    <div className="h-px bg-black/5 my-2" />
                    <div className="flex justify-between items-center text-xl font-bold">
                      <span>К оплате</span>
                      <span>{finalTotal} ₽</span>
                    </div>
                  </div>
                </div>
              )}

              {status === 'success' && (
                <div className="h-full flex flex-col items-center justify-center text-center space-y-6 py-12">
                  <div className="w-24 h-24 bg-green-500/20 rounded-full flex items-center justify-center text-green-500">
                    <CheckCircle2 size={60} />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold">Заказ оформлен!</h3>
                    <p className="opacity-60 mt-2">
                      {paymentMethod === 'delivery' 
                        ? 'Оплата при получении курьеру.' 
                        : paymentMethod === 'crypto' 
                          ? 'Транзакция в обработке.' 
                          : 'Оплата прошла успешно.'}
                      <br/> Ожидайте курьера.
                    </p>
                  </div>
                  <button 
                    onClick={() => {
                      onUpdateCart([]);
                      onClose();
                    }}
                    className="px-12 py-4 bg-blue-600 text-white rounded-full font-bold shadow-xl shadow-blue-600/20"
                  >
                    Вернуться на главную
                  </button>
                </div>
              )}

              {status === 'error' && (
                <div className="h-64 flex flex-col items-center justify-center text-center space-y-4">
                  <AlertCircle size={40} className="text-red-500" />
                  <p className="text-lg font-medium">Не удалось связаться со складом</p>
                  <button onClick={() => verifyStock()} className="text-blue-600 font-bold">Попробовать снова</button>
                </div>
              )}
            </div>

            {status === 'ready' && (
              <div className="p-6 pb-10">
                <button
                  onClick={handleConfirmOrder}
                  disabled={!isFormValid}
                  className={cn(
                    "w-full py-5 rounded-[24px] font-bold text-lg flex items-center justify-center gap-3 shadow-xl active:scale-[0.98] transition-all",
                    isFormValid
                      ? "bg-blue-600 text-white shadow-blue-600/20"
                      : "bg-gray-400 text-gray-200 cursor-not-allowed shadow-none"
                  )}
                >
                  {paymentMethod === 'delivery' ? 'Заказать' : 'Оплатить'} {finalTotal} ₽ <ArrowRight size={20} />
                </button>
                {!isFormValid && (
                  <p className="text-xs text-center opacity-40 mt-2">
                    Заполните все поля для продолжения
                  </p>
                )}
              </div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
