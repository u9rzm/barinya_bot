import { useRef, useEffect, PointerEvent, useMemo, useCallback } from 'react';
import { motion, AnimatePresence, useMotionValue, useDragControls, animate } from 'motion/react';
import { ChevronRight, Sparkles } from 'lucide-react';
import { cn } from '../utils/cn';
import { recommendationService } from '../services/recommendationService';
import { OptimizedImage } from './OptimizedImage';
import { throttle } from '../utils/throttle';

// Компонент каталога (Bottom Sheet): выбор категорий и просмотр товаров
export function CatalogSheet({ isOpen, onToggle, activeCategory, setActiveCategory, onSelectProduct, onCategoryChange, theme, currentProduct, categories = [], products = [] }: any) {
  const dragControls = useDragControls();
  const categoriesRef = useRef<HTMLDivElement>(null);
  const buttonsRef = useRef<(HTMLButtonElement | null)[]>([]);
  const contentRef = useRef<HTMLDivElement>(null);
  const startPointerEvent = useRef<PointerEvent | null>(null);
  const x = useMotionValue(0);

  const displayProducts = useMemo(() => {
    // Базовая фильтрация
    if (!currentProduct) return [];
    
    let filtered = products.filter((p: any) => p.category === activeCategory && p.id !== currentProduct.id);
    
    if (!isOpen) {
      const subFiltered = filtered.filter((p: any) => p.subcategory === currentProduct.subcategory);
      // Если в той же подкатегории есть товары - показываем их, иначе показываем всю категорию
      if (subFiltered.length > 0) {
        filtered = subFiltered;
      }
    }

    // Применяем рекомендации (сортировку)
    const isNewCategory = activeCategory === 'new';
    return recommendationService.getRecommendedProducts(filtered, null, isNewCategory);
  }, [isOpen, activeCategory, currentProduct, products]);

  const subcategories = Array.from(new Set(products.filter((p: any) => p.category === activeCategory).map((p: any) => p.subcategory || 'основное')));

  const handleContentPointerDown = (e: PointerEvent) => {
    if (contentRef.current && contentRef.current.scrollTop <= 0) {
      startPointerEvent.current = e;
    } else {
      startPointerEvent.current = null;
    }
  };

  const handleContentPointerMove = (e: PointerEvent) => {
    if (startPointerEvent.current) {
      const deltaY = e.clientY - startPointerEvent.current.clientY;
      const deltaX = Math.abs(e.clientX - startPointerEvent.current.clientX);
      
      // If moving down and more vertically than horizontally
      if (deltaY > 10 && deltaY > deltaX) {
        dragControls.start(startPointerEvent.current);
        startPointerEvent.current = null;
      } else if (deltaY < -5 || deltaX > 10) {
        // If moving up or horizontally, cancel the potential drag start
        startPointerEvent.current = null;
      }
    }
  };

  const centerCategory = (id: string, immediate = false) => {
    if (!categoriesRef.current) return;
    
    const targetIndex = categories.findIndex((cat: any) => cat.id === id);
    
    if (targetIndex !== -1) {
      const button = buttonsRef.current[targetIndex];
      if (button) {
        const containerWidth = categoriesRef.current.offsetWidth;
        const buttonLeft = button.offsetLeft;
        const buttonWidth = button.offsetWidth;
        
        const targetX = -(buttonLeft - (containerWidth / 2) + (buttonWidth / 2));
        
        // Calculate constraints
        const contentWidth = categoriesRef.current.scrollWidth;
        const minX = -(contentWidth - containerWidth);
        const maxX = 0;
        
        // Clamp targetX
        const clampedX = Math.max(minX, Math.min(maxX, targetX));
        
        if (immediate) {
          x.set(clampedX);
        } else {
          animate(x, clampedX, { 
            type: 'spring', 
            damping: 30, 
            stiffness: 150, 
            restDelta: 0.01 
          });
        }
      }
    }
  };

  // Initial centering when opened
  useEffect(() => {
    if (isOpen) {
      const timer = setTimeout(() => {
        centerCategory(activeCategory, true);
      }, 50);
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  // Re-center when activeCategory changes
  useEffect(() => {
    if (isOpen) {
      centerCategory(activeCategory);
    }
  }, [activeCategory, isOpen]);

  const handleCategoryClick = (id: string) => {
    setActiveCategory(id);
  };

  // Throttled category change to prevent rapid switching
  const throttledCategoryChange = useCallback(
    throttle((direction: number) => {
      onCategoryChange(direction);
    }, 300),
    [onCategoryChange]
  );

  return (
    <motion.div
      drag="y"
      dragControls={dragControls}
      dragListener={false}
      dragConstraints={{ top: 0, bottom: 0 }}
      dragElastic={0.1}
      onDragEnd={(_, info) => {
        if (info.offset.y > 80) onToggle();
      }}
      animate={{ 
        y: isOpen ? 0 : '66.66%',
        borderRadius: isOpen ? '0px' : '40px'
      }}
      transition={{ type: 'spring', damping: 30, stiffness: 300 }}
      className={cn(
        "fixed inset-0 z-[60] flex flex-col overflow-hidden",
        isOpen 
          ? (theme === 'dark' ? "bg-[#141414]" : "bg-[#e4e3e0]")
          : (theme === 'dark' 
              ? "bg-gradient-to-b from-transparent via-[#141414]/90 via-[5%] to-[#141414] to-[20%]" 
              : "bg-gradient-to-b from-transparent via-[#e4e3e0]/90 via-[5%] to-[#e4e3e0] to-[20%]")
      )}
    >
      {/* Header Area */}
      <div 
        onPointerDown={(e) => dragControls.start(e)}
        className={cn(
          "flex-shrink-0 cursor-ns-resize transition-all duration-500",
          isOpen ? "pt-12" : "pt-6"
        )}
      >
        <div className="px-6 pb-6 space-y-6">
          {/* Categories Carousel using Drag */}
          <div 
            className="overflow-hidden" 
            ref={categoriesRef}
            onPointerDown={(e) => e.stopPropagation()}
          >
            <motion.div 
              drag="x"
              dragConstraints={categoriesRef}
              dragElastic={0.1}
              dragMomentum={true}
              style={{ x }}
              className="flex gap-8 px-2"
            >
              {categories.map((cat: any, index: number) => (
                <button
                  key={cat.id}
                  ref={el => { buttonsRef.current[index] = el; }}
                  onClick={() => handleCategoryClick(cat.id)}
                  className={cn(
                    "whitespace-nowrap text-lg transition-all duration-300",
                    activeCategory === cat.id
                      ? (theme === 'dark' ? "text-white font-medium scale-110 text-glow" : "text-black font-medium scale-110 text-glow")
                      : (theme === 'dark' ? "text-white/40" : "text-black/40")
                  )}
                >
                  {cat.name}
                </button>
              ))}
            </motion.div>
          </div>

        {/* Subcategories */}
        <AnimatePresence>
          {isOpen && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="overflow-hidden" 
              onPointerDown={(e) => e.stopPropagation()}
            >
              <motion.div
                drag="x"
                dragConstraints={{ left: -300, right: 0 }}
                dragElastic={0.1}
                className="flex gap-6 px-2 pt-2"
              >
                {(subcategories as string[]).map((sub: string) => (
                  <button
                    key={sub}
                    className={cn(
                      "whitespace-nowrap text-[10px] uppercase tracking-widest font-bold transition-opacity",
                      theme === 'dark' ? "text-white" : "text-black",
                      sub === (currentProduct.subcategory || 'основное') ? "opacity-100" : "opacity-40"
                    )}
                  >
                    {sub}
                  </button>
                ))}
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>

      {/* Catalog Content */}
      <motion.div
        ref={contentRef}
        drag="x"
        dragConstraints={{ left: 0, right: 0 }}
        dragElastic={0.2}
        onDragEnd={(_, info) => {
          // Use throttled category change to prevent rapid switching
          if (info.offset.x < -100) throttledCategoryChange(1);
          else if (info.offset.x > 100) throttledCategoryChange(-1);
        }}
        onPointerDown={handleContentPointerDown}
        onPointerMove={handleContentPointerMove}
        className="flex-1 overflow-y-auto p-6 pt-0 space-y-6 no-scrollbar overscroll-behavior-y-contain"
      >
        <motion.div 
          variants={{
            hidden: { opacity: 0 },
            visible: {
              opacity: 1,
              transition: {
                staggerChildren: 0.05
              }
            }
          }}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-2 gap-4"
        >
          {displayProducts.map((p) => (
            <motion.div 
              key={p.id} 
              variants={{
                hidden: { opacity: 0, scale: 0.9, y: 10 },
                visible: { opacity: 1, scale: 1, y: 0 }
              }}
              onPointerDown={(e) => e.stopPropagation()}
              onClick={() => onSelectProduct(p)}
              className={cn(
                "rounded-[32px] relative overflow-hidden group active:scale-95 transition-transform aspect-[3/4] shadow-xl border",
                theme === 'dark' ? "bg-[#1a1a1a] border-white/5" : "bg-white border-black/5"
              )}
            >
              <motion.div
                layoutId={`product-image-${p.id}`}
                className="absolute inset-0"
              >
                <OptimizedImage src={p.image} alt={p.name} placeholder="pulse" />
              </motion.div>
              <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent" />
              
              {p.label && (
                <div 
                  style={{ backgroundColor: p.labelColor || '#2563eb' }}
                  className="absolute top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full text-[9px] text-white font-bold whitespace-nowrap rotate-[-5deg] z-10 shadow-lg"
                >
                  {p.label}
                </div>
              )}

              <div className="absolute bottom-0 left-0 right-0 p-4 pt-10 space-y-1">
                <p className="text-white text-xs font-medium leading-tight line-clamp-2 text-glow">{p.name}</p>
                <div className="flex justify-between items-center">
                  <p className="text-white/90 text-[11px] font-bold">{p.price} ₽</p>
                  <ChevronRight size={14} className="text-white/40" />
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </motion.div>
    </motion.div>
  );
}
