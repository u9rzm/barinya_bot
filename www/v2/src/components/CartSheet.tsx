import { motion, AnimatePresence } from 'motion/react';
import { X, Trash2, ShoppingBag, ArrowRight } from 'lucide-react';
import { CartItem } from '../constants/types';
import { cn } from '../utils/cn';
import { OptimizedImage } from './OptimizedImage';

interface CartSheetProps {
  isOpen: boolean;
  onClose: () => void;
  cart: CartItem[];
  onUpdateQuantity: (index: number, quantity: number) => void;
  onRemove: (index: number) => void;
  onOpenCheckout: () => void;
  theme: 'light' | 'dark';
}

export function CartSheet({ isOpen, onClose, cart, onUpdateQuantity, onRemove, onOpenCheckout, theme }: CartSheetProps) {
  const getItemPrice = (item: CartItem) => {
    const options = Array.isArray(item.selectedOptions) ? item.selectedOptions : [];
    const addonsPrice = options.reduce((acc, opt) => acc + (opt.price || 0), 0);
    return (item.product.price + addonsPrice) * item.quantity;
  };

  const total = cart.reduce((acc, item) => acc + getItemPrice(item), 0);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[150]"
          />
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className={cn(
              "fixed inset-x-0 bottom-0 z-[160] rounded-t-[40px] max-h-[90vh] flex flex-col",
              theme === 'dark' ? "bg-[#1a1a1a] text-white" : "bg-[#f5f5f0] text-black"
            )}
          >
            <div className="w-12 h-1.5 bg-black/10 rounded-full mx-auto mt-4 mb-2" />
            
            <header className="p-6 flex justify-between items-center border-b border-black/5">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center text-white">
                  <ShoppingBag size={20} />
                </div>
                <div>
                  <h2 className="text-xl font-bold">Корзина</h2>
                  <p className="text-xs opacity-50">{cart.length} товаров</p>
                </div>
              </div>
              <button 
                onClick={onClose}
                className="w-10 h-10 rounded-full bg-black/5 flex items-center justify-center"
              >
                <X size={20} />
              </button>
            </header>

            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {cart.length === 0 ? (
                <div className="h-64 flex flex-col items-center justify-center text-center space-y-4">
                  <div className="w-20 h-20 bg-black/5 rounded-full flex items-center justify-center opacity-20">
                    <ShoppingBag size={40} />
                  </div>
                  <p className="text-lg font-medium opacity-40">Ваша корзина пуста</p>
                  <button 
                    onClick={onClose}
                    className="px-8 py-3 bg-blue-600 text-white rounded-full font-medium"
                  >
                    Перейти к покупкам
                  </button>
                </div>
              ) : (
                cart.map((item, index) => (
                  <div key={`${item.product.id}-${index}`} className="flex gap-4 items-start">
                    <div className="w-20 h-20 rounded-2xl overflow-hidden bg-black/5 flex-shrink-0">
                      <OptimizedImage src={item.product.image} alt={item.product.name} placeholder="pulse" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-bold truncate">{item.product.name}</h3>
                      {Array.isArray(item.selectedOptions) && item.selectedOptions.length > 0 && (
                        <p className="text-[10px] opacity-40 leading-tight mt-1">
                          {item.selectedOptions.map(o => o.name).join(', ')}
                        </p>
                      )}
                      <p className="text-sm font-bold mt-1">{getItemPrice(item) / item.quantity} ₽</p>
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      <div className="flex items-center gap-3 bg-black/5 rounded-full p-1">
                        <button
                          onClick={() => onUpdateQuantity(index, item.quantity - 1)}
                          aria-label="Уменьшить количество"
                          className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-black/5"
                        >
                          -
                        </button>
                        <span className="w-4 text-center font-bold">{item.quantity}</span>
                        <button
                          onClick={() => onUpdateQuantity(index, item.quantity + 1)}
                          aria-label="Увеличить количество"
                          className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-black/5"
                        >
                          +
                        </button>
                      </div>
                      <button
                        onClick={() => onRemove(index)}
                        aria-label="Удалить товар из корзины"
                        className="text-[10px] text-red-500 opacity-40 hover:opacity-100 flex items-center gap-1"
                      >
                        <Trash2 size={12} aria-hidden="true" /> Удалить
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>

            {cart.length > 0 && (
              <div className="p-6 border-t border-black/5 space-y-4 bg-white/5 backdrop-blur-md">
                <div className="flex justify-between items-center text-lg">
                  <span className="opacity-50">Итого:</span>
                  <span className="font-bold text-2xl">{total} ₽</span>
                </div>
                <button 
                  className="w-full bg-blue-600 text-white py-4 rounded-full font-bold text-base flex items-center justify-center gap-2 shadow-xl shadow-blue-600/20 active:scale-[0.98] transition-all"
                  onClick={onOpenCheckout}
                >
                  Оплатить <ArrowRight size={18} />
                </button>
              </div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
