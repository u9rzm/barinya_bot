import { useState, useRef, useEffect, Suspense, lazy, memo } from 'react';
import { motion, AnimatePresence, useMotionValue, useTransform, animate } from 'motion/react';
import { User, Moon, Sun, ShoppingBag, Plus, Globe } from 'lucide-react';
import { cn } from '../utils/cn';
import { CircleMenuAction } from './UI';
import { CatalogSheet } from './CatalogSheet';
import { OptimizedVideo } from './OptimizedVideo';
import { OptimizedImage } from './OptimizedImage';
import { TelegramUser } from '../auth';
import { CartItem, Category, Product } from '../constants/types';

// Lazy load CartSheet for code splitting
const CartSheetLazy = lazy(() => import('./CartSheet').then(module => ({ default: module.CartSheet })));

// Главный экран: Hero-секция, переключение категорий свайпом и профиль пользователя
export const MainPage = memo(function MainPage({
  activeCategory,
  setActiveCategory,
  currentProduct,
  onOpenProduct,
  onCategoryChange,
  isCatalogOpen,
  setIsCatalogOpen,
  onSelectProduct,
  telegramUser,
  isAuthenticated,
  theme,
  setTheme,
  isProfileMenuOpen,
  setIsProfileMenuOpen,
  cart = [],
  onUpdateCartQuantity,
  onRemoveFromCart,
  onOpenCheckout,
  categories = [],
  products = [],
  isProductDetailOpen
}: {
  activeCategory: string;
  setActiveCategory: (id: string) => void;
  currentProduct: Product;
  onOpenProduct: () => void;
  onCategoryChange: (dir: number) => void;
  isCatalogOpen: boolean;
  setIsCatalogOpen: (open: boolean) => void;
  onSelectProduct: (p: Product) => void;
  telegramUser: TelegramUser | null;
  isAuthenticated: boolean;
  theme: 'light' | 'dark';
  setTheme: (t: 'light' | 'dark') => void;
  isProfileMenuOpen: boolean;
  setIsProfileMenuOpen: (open: boolean) => void;
  cart: CartItem[];
  onUpdateCartQuantity: (i: number, q: number) => void;
  onRemoveFromCart: (i: number) => void;
  onOpenCheckout: () => void;
  categories: Category[];
  products: Product[];
  isProductDetailOpen: boolean;
}) {
  const x = useMotionValue(0);
  const isDragging = useRef(false);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [isCurrentVideoLoaded, setIsCurrentVideoLoaded] = useState(false);
  const prevCategoryRef = useRef(activeCategory);
  const lastProductId = useRef<string | null>(null);
  const wasProductDetailOpen = useRef(isProductDetailOpen);

  const background = useTransform(
    x,
    [-200, 0, 200],
    theme === 'dark' ? ["#9a4d18", "#141414", "#3d3d2b"] : ["#f27d26", "#e4e3e0", "#5A5A40"]
  );

  // Reset video loaded state when category changes or returning from product detail
  useEffect(() => {
    if (activeCategory !== prevCategoryRef.current) {
      setIsCurrentVideoLoaded(false);
      prevCategoryRef.current = activeCategory;
    }
    // Reset video state when closing product detail to force reload
    if (!isProductDetailOpen && wasProductDetailOpen.current) {
      setIsCurrentVideoLoaded(false);
    }
    wasProductDetailOpen.current = isProductDetailOpen;
  }, [activeCategory, isProductDetailOpen]);

  if (!currentProduct) return null;

  // Reset x immediately during render to ensure seamless transition
  if (currentProduct?.id !== lastProductId.current) {
    x.set(0);
    lastProductId.current = currentProduct.id;
    setIsCurrentVideoLoaded(false);
  }

  const handleDragStart = () => {
    isDragging.current = true;
  };

  const handleDragEnd = (_: any, info: any) => {
    // Small delay to ensure click handler doesn't fire immediately after drag
    setTimeout(() => {
      isDragging.current = false;
    }, 50);

    const width = window.innerWidth;
    const threshold = width * 0.15;
    const velocity = info.velocity.x;

    if (info.offset.x < -threshold || velocity < -300) {
      // Animate to next
      animate(x, -width, {
        type: "spring",
        stiffness: 400,
        damping: 40,
        restDelta: 0.5,
        onComplete: () => {
          onCategoryChange(1);
          setIsCurrentVideoLoaded(false);
        }
      });
    } else if (info.offset.x > threshold || velocity > 300) {
      // Animate to prev
      animate(x, width, {
        type: "spring",
        stiffness: 400,
        damping: 40,
        restDelta: 0.5,
        onComplete: () => {
          onCategoryChange(-1);
          setIsCurrentVideoLoaded(false);
        }
      });
    } else {
      // Snap back to center
      animate(x, 0, {
        type: "spring",
        stiffness: 400,
        damping: 40
      });
    }
  };

  const handleClick = () => {
    if (!isDragging.current) {
      onOpenProduct();
    }
  };

  // Preload next and previous products' videos
  const currentIndex = categories.findIndex((c: any) => c.id === activeCategory);
  const nextIndex = (currentIndex + 1) % categories.length;
  const prevIndex = (currentIndex - 1 + categories.length) % categories.length;
  const nextProduct = products.find((p: any) => p.category === categories[nextIndex].id);
  const prevProduct = products.find((p: any) => p.category === categories[prevIndex].id);

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      style={{ background }}
      drag={isCatalogOpen ? false : "y"}
      dragConstraints={{ top: 0, bottom: 0 }}
      dragElastic={0.05}
      onDragEnd={(_, info) => {
        if (info.offset.y < -50) setIsCatalogOpen(true);
      }}
      className="relative h-full flex flex-col"
    >
      {/* Header - Overlayed */}
      <header className="absolute top-0 left-0 right-0 flex justify-between items-start p-6 pt-12 z-50 pointer-events-none">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-xl">🐳</span>
          </div>
          <div>
            <h2 className="font-semibold text-sm text-glow">Cake Home</h2>
            <p className="text-[10px] opacity-60">до 17:30</p>
          </div>
        </div>
        
        <div className="flex flex-col items-end gap-3 pointer-events-auto relative">
          {/* Invisible overlay to catch clicks outside the menu */}
          <AnimatePresence>
            {isProfileMenuOpen && (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-[55] bg-transparent"
                onClick={() => setIsProfileMenuOpen(false)}
              />
            )}
          </AnimatePresence>

          <motion.button
            onPointerDown={(e) => e.stopPropagation()}
            onClick={() => setIsProfileMenuOpen(!isProfileMenuOpen)}
            layout
            className={cn(
              "h-10 bg-white/50 backdrop-blur-md rounded-full flex items-center gap-3 border border-white/20 shadow-lg px-0 z-[60]",
              isProfileMenuOpen ? "pl-4 pr-0" : "w-10 justify-center"
            )}
          >
            <AnimatePresence mode="wait">
              {isAuthenticated && isProfileMenuOpen && (
                <motion.span
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  className="text-sm font-medium whitespace-nowrap overflow-hidden text-black"
                >
                  {telegramUser ? `@${telegramUser.username || telegramUser.firstName || 'User'}` : 'Гость'}
                </motion.span>
              )}
            </AnimatePresence>

            <motion.div
              layout="position"
              className="relative flex-shrink-0 w-10 h-10 flex items-center justify-center rounded-full overflow-hidden"
            >
              {isAuthenticated && telegramUser?.photoUrl ? (
                <OptimizedImage src={telegramUser.photoUrl} alt={String(telegramUser.firstName || 'User')} placeholder="pulse" className="!w-10 !h-10 !rounded-full" />
              ) : (
                <User size={20} className={cn(
                  "text-black/70",
                  isAuthenticated && "text-blue-600"
                )} />
              )}
              {!isAuthenticated && (
                <div className="absolute top-1 right-1 w-3 h-3 bg-white rounded-full flex items-center justify-center border border-black/10 shadow-sm z-10">
                  <Plus size={8} className="text-black" />
                </div>
              )}
            </motion.div>
          </motion.button>

          {/* Floating Profile Menu Icons */}
          <AnimatePresence>
            {isProfileMenuOpen && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="absolute top-full right-0 mt-2 flex flex-col gap-2 z-[60]"
                onClick={(e) => e.stopPropagation()}
              >
                <CircleMenuAction 
                  icon={
                    <div className="relative">
                      <ShoppingBag size={20} />
                      {cart.length > 0 && (
                        <div className="absolute -top-1 -right-1 w-4 h-4 bg-blue-600 text-white text-[10px] font-bold rounded-full flex items-center justify-center border border-white/20">
                          {cart.reduce((acc: number, item: any) => acc + item.quantity, 0)}
                        </div>
                      )}
                    </div>
                  } 
                  onClick={() => {
                    setIsCartOpen(true);
                    setIsProfileMenuOpen(false);
                  }}
                  theme={theme}
                />
                <CircleMenuAction 
                  icon={theme === 'light' ? <Moon size={20} /> : <Sun size={20} />} 
                  onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
                  theme={theme}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </header>

      {/* Hero Section - Full Width & Top Aligned */}
      <div className="absolute top-0 left-0 right-0 bottom-[22%] overflow-hidden">
        <motion.div 
          style={{ x }}
          drag="x"
          dragConstraints={{ left: -window.innerWidth, right: window.innerWidth }}
          dragElastic={0.02}
          onDragStart={handleDragStart}
          onDragEnd={handleDragEnd}
          onPointerDown={(e) => e.stopPropagation()}
          className="relative w-full h-full flex"
        >
          {/* Previous Product Preview */}
          <div 
            className="absolute top-0 bottom-0 w-full" 
            style={{ left: '-100%' }}
          >
            {prevProduct && (
              <div className="w-full h-full relative">
                <OptimizedVideo 
                  src={prevProduct.videoUrl} 
                  poster={prevProduct.image} 
                  active={false}
                  preload={isCurrentVideoLoaded}
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-black/10" />
              </div>
            )}
          </div>

          {/* Current Product */}
          <div 
            className="relative w-full h-full flex-shrink-0" 
            onClick={handleClick}
          >
            <motion.div 
              layoutId={`product-image-${currentProduct.id}`}
              className="absolute inset-0"
            >
              <OptimizedVideo 
                src={currentProduct.videoUrl} 
                poster={currentProduct.image} 
                active={!isCatalogOpen && !isProductDetailOpen}
                className="w-full h-full object-cover"
                onLoaded={() => setIsCurrentVideoLoaded(true)}
              />
            </motion.div>
            <motion.div 
              key={currentProduct.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.5 }}
              className="absolute left-0 right-0 text-center z-10 bottom-12"
            >
              <h1 className="text-2xl font-bold leading-tight px-10 text-glow-orange">
                {currentProduct.name}
              </h1>
            </motion.div>
            <div className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-black/40 via-black/20 to-transparent pointer-events-none" />
          </div>

          {/* Next Product Preview */}
          <div 
            className="absolute top-0 bottom-0 w-full" 
            style={{ left: '100%' }}
          >
            {nextProduct && (
              <div className="w-full h-full relative">
                <OptimizedVideo 
                  src={nextProduct.videoUrl} 
                  poster={nextProduct.image} 
                  active={false}
                  preload={isCurrentVideoLoaded}
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-black/10" />
              </div>
            )}
          </div>
        </motion.div>
      </div>

      {/* Bottom Sheet Catalog */}
      <CatalogSheet 
        isOpen={isCatalogOpen}
        onToggle={() => setIsCatalogOpen(!isCatalogOpen)}
        activeCategory={activeCategory}
        setActiveCategory={setActiveCategory}
        onSelectProduct={onSelectProduct}
        onCategoryChange={onCategoryChange}
        theme={theme}
        currentProduct={currentProduct}
        categories={categories}
        products={products}
      />

      {/* Cart Sheet */}
      <AnimatePresence>
        {isCartOpen && (
          <Suspense fallback={null}>
            <CartSheetLazy
              isOpen={isCartOpen}
              onClose={() => setIsCartOpen(false)}
              cart={cart}
              onUpdateQuantity={onUpdateCartQuantity}
              onRemove={onRemoveFromCart}
              onOpenCheckout={() => {
                setIsCartOpen(false);
                onOpenCheckout();
              }}
              theme={theme}
            />
          </Suspense>
        )}
      </AnimatePresence>

      {/* Floating Checkout Button */}
      <AnimatePresence>
        {cart.length > 0 && !isCatalogOpen && !isCartOpen && (
          <motion.div
            initial={{ y: 100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 100, opacity: 0 }}
            className="fixed bottom-10 left-1/2 -translate-x-1/2 z-[80]"
          >
            <button
              onClick={onOpenCheckout}
              className="bg-blue-600 text-white py-3.5 px-6 rounded-full font-bold text-base flex items-center gap-3 shadow-2xl shadow-blue-600/40 active:scale-[0.98] transition-all whitespace-nowrap"
            >
              <ShoppingBag size={18} />
              <span>
                {cart.reduce((acc: number, item: any) => acc + (item.product.price + (item.selectedOptions || []).reduce((a: number, o: any) => a + (o.price || 0), 0)) * item.quantity, 0)} ₽
              </span>
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}, (prevProps, nextProps) => {
  // Custom comparison для предотвращения лишних рендеров
  return prevProps.activeCategory === nextProps.activeCategory
    && prevProps.currentProduct?.id === nextProps.currentProduct?.id
    && prevProps.theme === nextProps.theme
    && prevProps.isCatalogOpen === nextProps.isCatalogOpen
    && prevProps.isProductDetailOpen === nextProps.isProductDetailOpen
    && prevProps.cart === nextProps.cart
    && prevProps.categories === nextProps.categories
    && prevProps.products === nextProps.products;
});
