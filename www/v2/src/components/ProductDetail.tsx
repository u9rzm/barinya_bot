import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence, useMotionValue, useTransform } from 'motion/react';
import { X, ChevronDown, Plus, Heart, ShoppingBag } from 'lucide-react';
import { Product, Addon, AddonOption, CartItem } from '../constants/types';
import { cn } from '../utils/cn';
import { OptimizedVideo } from './OptimizedVideo';
import { OptimizedImage } from './OptimizedImage';

// Детальная страница товара: описание, КБЖУ и выбор добавок
export function ProductDetail({ 
  product, 
  onClose, 
  onOrder,
  onAddToCart,
  cart
}: { 
  product: Product, 
  onClose: () => void, 
  onOrder: () => void,
  onAddToCart: (quantity: number, options: AddonOption[]) => void,
  cart: CartItem[]
}) {
  const addonsRef = useRef<HTMLDivElement>(null);
  const [addonConstraints, setAddonConstraints] = useState({ left: 0, right: 0 });
  const [isDescriptionOpen, setIsDescriptionOpen] = useState(false);
  const [isLiked, setIsLiked] = useState(false);
  const [quantity, setQuantity] = useState(1);
  const [selectedOptions, setSelectedOptions] = useState<{option: AddonOption, quantity: number, addonId: string}[]>(() => {
    const initial: {option: AddonOption, quantity: number, addonId: string}[] = [];
    if (product?.addons) {
      product.addons.forEach(addon => {
        // По умолчанию выбираем первую опцию для каждой группы с количеством 1
        // (например, обычное молоко)
        initial.push({ option: addon.options[0], quantity: 1, addonId: addon.id });
      });
    }
    return initial;
  });
  const [activeAddon, setActiveAddon] = useState<Addon | null>(null);

  const dragY = useMotionValue(0);
  const bgOpacity = useTransform(dragY, [0, 300], [1, 0]);
  const contentOpacity = useTransform(dragY, [0, 150], [1, 0]);

  useEffect(() => {
    if (addonsRef.current) {
      const containerWidth = addonsRef.current.offsetWidth;
      const contentWidth = addonsRef.current.scrollWidth;
      setAddonConstraints({ left: -(contentWidth - containerWidth + 20), right: 0 });
    }
  }, [product.addons]);

  const handleUpdateOptionQuantity = (addonId: string, option: AddonOption, delta: number) => {
    setSelectedOptions(prev => {
      const selectionType = option.selectionType || 'single';
      const existingIndex = prev.findIndex(item => item.option.id === option.id && item.addonId === addonId);
      
      // 1. If selecting a 'single' option (like "None" or a specific Milk)
      if (selectionType === 'single') {
        if (delta <= 0) return prev; // Can't decrement a single choice to 0 manually
        // Selecting a single choice clears all other options in this group
        return [
          ...prev.filter(item => item.addonId !== addonId),
          { option, quantity: 1, addonId }
        ];
      }

      // 2. If selecting a 'toggle' or 'multiple' option
      let newOptions = [...prev];
      
      // Remove any 'single' options (like "None") from this group when adding a non-single option
      if (delta > 0) {
        newOptions = newOptions.filter(item => {
          if (item.addonId !== addonId) return true;
          const itemSelectionType = item.option.selectionType || 'single';
          return itemSelectionType !== 'single';
        });
      }

      if (existingIndex > -1) {
        const item = newOptions[existingIndex];
        const newQuantity = selectionType === 'toggle' 
          ? (delta > 0 ? 1 : 0) // Toggle is binary
          : item.quantity + delta;
        
        if (newQuantity <= 0) {
          const filtered = newOptions.filter((_, i) => i !== existingIndex);
          // If group becomes empty, add the first 'single' option (usually "None") back
          const groupStillHasOptions = filtered.some(i => i.addonId === addonId);
          if (!groupStillHasOptions) {
            const addon = product.addons?.find(a => a.id === addonId);
            const defaultOpt = addon?.options.find(o => (o.selectionType || 'single') === 'single');
            if (defaultOpt) {
              return [...filtered, { option: defaultOpt, quantity: 1, addonId }];
            }
          }
          return filtered;
        }
        
        newOptions[existingIndex] = { ...item, quantity: newQuantity };
        return newOptions;
      } else if (delta > 0) {
        return [...newOptions, { option, quantity: selectionType === 'toggle' ? 1 : delta, addonId }];
      }
      
      return prev;
    });
  };

  const getGroupSummary = (addonId: string) => {
    const groupOptions = selectedOptions.filter(item => item.addonId === addonId);
    if (groupOptions.length === 0) return "Нет";
    
    // If "None" is selected, just show that
    if (groupOptions.length === 1 && groupOptions[0].option.id.startsWith('none')) return "Нет";

    const first = groupOptions[0];
    const firstName = first.option.name;
    const firstQty = first.quantity > 1 ? ` x${first.quantity}` : '';
    
    if (groupOptions.length > 1) {
      return `${firstName}${firstQty} +${groupOptions.length - 1}`;
    }
    
    return `${firstName}${firstQty}`;
  };

  const getGroupImage = (addonId: string) => {
    const groupOptions = selectedOptions.filter(item => item.addonId === addonId);
    return groupOptions[0]?.option.image || product.image;
  };

  const calculateBaseTotal = () => {
    const cartBaseTotal = cart.reduce((acc, item) => {
      return acc + item.product.price * item.quantity;
    }, 0);

    const currentProductBase = product.price * quantity;
    return cartBaseTotal + currentProductBase;
  };

  const getOptionPrice = (option: AddonOption) => {
    if (!option.price) return 0;
    const baseTotal = calculateBaseTotal();
    if (option.freeThreshold && baseTotal >= option.freeThreshold) return 0;
    return option.price;
  };

  const calculateSelectedAddonsPrice = () => {
    return selectedOptions.reduce((acc, item) => {
      return acc + getOptionPrice(item.option) * item.quantity;
    }, 0);
  };

  const totalPrice = (product.price * quantity) + calculateSelectedAddonsPrice();

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.3
      }
    }
  } as const;

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { type: 'spring' as const, damping: 25, stiffness: 200 }
    }
  } as const;

  const headerVariants = {
    hidden: { opacity: 0, y: -20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { type: 'spring' as const, damping: 25, stiffness: 200 }
    }
  } as const;

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      drag="y"
      dragConstraints={{ top: 0, bottom: 0 }}
      dragElastic={0.2}
      style={{ y: dragY }}
      onDragEnd={(_, info) => {
        if (info.offset.y > 150) onClose();
      }}
      className="fixed inset-0 z-[100] flex flex-col overflow-hidden"
    >
      {/* Background with dynamic opacity */}
      <motion.div 
        style={{ opacity: bgOpacity }}
        className="absolute inset-0 bg-[#e4e3e0]"
      />

      {/* Full Screen Background Image/Video - Shared Element */}
      <motion.div 
        layoutId={`product-image-${product.id}`}
        className="absolute inset-0 z-0"
      >
        <OptimizedVideo 
          src={product.videoUrl} 
          poster={product.image} 
        />
        {/* Overlays for readability */}
        <div className="absolute inset-0 bg-black/10 pointer-events-none" />
        <div className="absolute inset-x-0 top-0 h-64 bg-gradient-to-b from-black/40 to-transparent pointer-events-none" />
        <div className="absolute inset-x-0 bottom-0 h-96 bg-gradient-to-t from-black/40 to-transparent pointer-events-none" />
      </motion.div>
      
      {/* Content Overlay */}
      <motion.div 
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        style={{ opacity: contentOpacity }}
        className="relative z-10 h-full flex flex-col"
      >
        {/* Header */}
        <motion.header variants={headerVariants} className="flex justify-between items-center p-6 pt-12">
          <div className="flex-1 text-center text-white text-glow">
            <h2 className="text-lg font-medium">{product.description.split(' ')[0]}</h2>
            <p className="text-sm opacity-80">{product.description.split(' ').slice(1).join(' ')}</p>
          </div>
          <button
            onClick={() => setIsLiked(!isLiked)}
            aria-label={isLiked ? 'Удалить из избранного' : 'Добавить в избранное'}
            aria-pressed={isLiked}
            className="w-10 h-10 bg-white/20 backdrop-blur-md rounded-full flex items-center justify-center absolute right-6 border border-white/20 transition-colors"
          >
            <Heart size={20} className={cn("transition-colors", isLiked ? "fill-red-500 text-red-500" : "text-white")} aria-hidden="true" />
          </button>
        </motion.header>

        {/* Nutritional Stats */}
        <motion.div variants={itemVariants} className="px-6 flex justify-between text-center text-white drop-shadow-lg mt-4">
          <div>
            <p className="font-medium">{product.calories} ккал</p>
            <p className="text-[10px] opacity-70 uppercase">энергия</p>
          </div>
          <div>
            <p className="font-medium">{product.proteins} г</p>
            <p className="text-[10px] opacity-70 uppercase">белки</p>
          </div>
          <div>
            <p className="font-medium">{product.fats} г</p>
            <p className="text-[10px] opacity-70 uppercase">жиры</p>
          </div>
          <div>
            <p className="font-medium">{product.carbs} г</p>
            <p className="text-[10px] opacity-70 uppercase">углеводы</p>
          </div>
        </motion.div>

        {/* Description Button */}
        <motion.div variants={itemVariants} className="flex justify-center mt-6 relative">
          <button 
            onClick={() => setIsDescriptionOpen(!isDescriptionOpen)}
            className="flex items-center gap-1 px-4 py-1.5 bg-white/20 backdrop-blur-md rounded-full text-xs font-medium text-white border border-white/10"
          >
            Описание <ChevronDown size={14} className={cn("transition-transform duration-300", isDescriptionOpen && "rotate-180")} />
          </button>

          <AnimatePresence>
            {isDescriptionOpen && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9, y: 10 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9, y: 10 }}
                drag="y"
                dragConstraints={{ top: 0, bottom: 0 }}
                onDragEnd={(_, info) => {
                  if (info.offset.y > 50) setIsDescriptionOpen(false);
                }}
                onClick={() => setIsDescriptionOpen(false)}
                className="absolute top-full left-1/2 -translate-x-1/2 mt-4 w-[85%] bg-white/10 backdrop-blur-xl border border-white/10 rounded-3xl p-6 text-white text-sm leading-relaxed shadow-2xl z-30 cursor-pointer"
              >
                <div className="w-8 h-1 bg-white/20 rounded-full mx-auto mb-4" />
                {product.longDescription || product.name}
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Spacer to push content to bottom */}
        <div className="flex-1" />

        {/* Bottom Section - Add-ons and Order Button */}
        <motion.div variants={itemVariants} className="p-6 pb-10 space-y-6">
          <div className="w-full overflow-hidden" ref={addonsRef}>
            <motion.div 
              drag={addonConstraints.left < 0 ? "x" : false}
              dragConstraints={addonConstraints}
              dragElastic={0.1}
              className={cn(
                "flex gap-3 py-2 w-max min-w-full",
                addonConstraints.left >= 0 ? "justify-center" : "justify-start"
              )}
            >
              {product.addons?.map((addon) => (
                <div 
                  key={addon.id} 
                  onClick={() => setActiveAddon(addon)}
                  className="min-w-[65px] aspect-square bg-white/10 backdrop-blur-md rounded-2xl p-2 flex flex-col justify-between border border-white/10 cursor-pointer active:scale-95 transition-transform"
                >
                  <div className="w-7 h-7 rounded-full bg-white/5 flex items-center justify-center self-center mt-1 overflow-hidden">
                    <img 
                      src={getGroupImage(addon.id)} 
                      className="w-full h-full object-cover" 
                    />
                  </div>
                  <p className="text-[7px] text-center font-medium leading-tight text-white uppercase tracking-tighter truncate">
                    {getGroupSummary(addon.id)}
                  </p>
                </div>
              ))}
            </motion.div>
          </div>

          <div className="flex gap-4 items-center">
            <div className="flex-1 bg-white/10 backdrop-blur-md border border-white/10 text-white rounded-full py-4 px-4 flex items-center justify-between font-medium">
              <button 
                onClick={() => setQuantity(prev => Math.max(1, prev - 1))}
                className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-white/10 transition-colors"
              >
                -
              </button>
              <span className="text-lg">{quantity}</span>
              <button 
                onClick={() => setQuantity(prev => prev + 1)}
                className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-white/10 transition-colors"
              >
                +
              </button>
            </div>
            <button 
              onClick={() => {
                const flatOptions: AddonOption[] = [];
                selectedOptions.forEach(item => {
                  for (let i = 0; i < item.quantity; i++) {
                    flatOptions.push(item.option);
                  }
                });
                onAddToCart(quantity, flatOptions);
                onClose();
              }}
              className="flex-[2] bg-blue-600 text-white rounded-full py-4 px-8 flex justify-center items-center gap-2 font-medium shadow-lg shadow-blue-600/30 active:scale-95 transition-transform"
            >
              <ShoppingBag size={20} /> 
              <span>
                {totalPrice} ₽
              </span>
            </button>
          </div>
        </motion.div>
      </motion.div>

      {/* Addon Selection Menu */}
      <AnimatePresence>
        {activeAddon && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100] flex items-end justify-center bg-black/40 backdrop-blur-sm p-4"
            onClick={() => setActiveAddon(null)}
          >
            <motion.div
              initial={{ y: 100 }}
              animate={{ y: 0 }}
              exit={{ y: 100 }}
              className="w-full max-w-md bg-[#1a1a1a] rounded-[32px] p-6 space-y-6"
              onClick={e => e.stopPropagation()}
            >
              <div className="flex justify-between items-center">
                <h3 className="text-white text-lg font-medium">{activeAddon.name}</h3>
                <button 
                  onClick={() => setActiveAddon(null)} 
                  aria-label="Закрыть"
                  className="text-white/40 hover:text-white transition-colors"
                >
                  <X size={20} aria-hidden="true" />
                </button>
              </div>
              <div className="grid grid-cols-1 gap-3 max-h-[60vh] overflow-y-auto pr-2">
                {activeAddon.options.map(option => {
                  const selectedItem = selectedOptions.find(item => item.option.id === option.id && item.addonId === activeAddon.id);
                  const currentQty = selectedItem?.quantity || 0;
                  const st = option.selectionType || 'single';
                  const isSingle = st === 'single';
                  const isToggle = st === 'toggle';
                  const isMultiple = st === 'multiple';
                  
                  return (
                    <div 
                      key={option.id}
                      onClick={() => {
                        if (isSingle || isToggle) {
                          handleUpdateOptionQuantity(activeAddon.id, option, currentQty > 0 && isToggle ? -1 : 1);
                        }
                      }}
                      className={cn(
                        "flex items-center justify-between p-3 rounded-2xl transition-all border",
                        currentQty > 0 ? "bg-blue-600/20 border-blue-600/50" : "bg-white/5 border-transparent",
                        (isSingle || isToggle) && "cursor-pointer active:scale-[0.98]"
                      )}
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-full overflow-hidden bg-white/10 flex-shrink-0">
                          <OptimizedImage src={option.image} alt={option.name} placeholder="pulse" className="!w-12 !h-12 !aspect-square" />
                        </div>
                        <div>
                          <p className="text-sm text-white font-medium">{option.name}</p>
                          {option.price && (
                            <p className="text-xs text-white/60">
                              {getOptionPrice(option) === 0 ? (
                                <span className="text-green-400 font-bold">Бесплатно</span>
                              ) : (
                                `+${option.price} ₽`
                              )}
                              {option.freeThreshold && getOptionPrice(option) !== 0 && (
                                <span className="ml-1 opacity-40">(от {option.freeThreshold} ₽ — 0 ₽)</span>
                              )}
                            </p>
                          )}
                        </div>
                      </div>
                      
                      {isMultiple ? (
                        <div className="flex items-center gap-3 bg-white/10 rounded-full p-1">
                          <button 
                            onClick={(e) => {
                              e.stopPropagation();
                              handleUpdateOptionQuantity(activeAddon.id, option, -1);
                            }}
                            className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-white/10 text-white"
                          >
                            -
                          </button>
                          <span className="text-white font-medium min-w-[20px] text-center">{currentQty}</span>
                          <button 
                            onClick={(e) => {
                              e.stopPropagation();
                              handleUpdateOptionQuantity(activeAddon.id, option, 1);
                            }}
                            className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-white/10 text-white"
                          >
                            +
                          </button>
                        </div>
                      ) : (
                        <div className={cn(
                          "w-6 h-6 flex items-center justify-center transition-colors border-2",
                          isSingle ? "rounded-full" : "rounded-md",
                          currentQty > 0 ? "border-blue-500 bg-blue-500" : "border-white/20"
                        )}>
                          {currentQty > 0 && (
                            isSingle ? (
                              <div className="w-2 h-2 rounded-full bg-white" />
                            ) : (
                              <div className="w-3 h-3 text-white flex items-center justify-center">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" className="w-full h-full">
                                  <polyline points="20 6 9 17 4 12" />
                                </svg>
                              </div>
                            )
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}