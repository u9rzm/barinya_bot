import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { MapPin, ChevronRight, Sparkles, CheckCircle2, WifiOff } from 'lucide-react';
import { cn } from '../utils/cn';
import { mediaPreloader, MediaLoadProgress } from '../services/mediaPreloader';

const CITIES = [
  { id: 'irkutsk', name: 'Иркутск' },
  { id: 'moscow', name: 'Москва' },
  { id: 'spb', name: 'Санкт-Петербург' },
  { id: 'kazan', name: 'Казань' },
];

interface LoadingScreenProps {
  onComplete: (city: string) => void;
  theme: 'light' | 'dark';
  isAppReady: boolean;
  hasCity: boolean;
  products?: Array<{ videoUrl?: string; image: string }>;
}

export function LoadingScreen({ onComplete, theme, isAppReady, hasCity, products = [] }: LoadingScreenProps) {
  const [step, setStep] = useState<'greeting' | 'promo' | 'loading' | 'ready'>('greeting');
  const [selectedCity, setSelectedCity] = useState<string | null>(null);
  const [mediaProgress, setMediaProgress] = useState<MediaLoadProgress>({ total: 0, loaded: 0, percentage: 0, criticalLoaded: false });
  const [hasNetworkIssues, setHasNetworkIssues] = useState(false);

  // Initialize media preloader and start preloading critical products
  useEffect(() => {
    const initPreload = async () => {
      await mediaPreloader.initialize();
      
      if (products.length > 0) {
        // Preload first 3 products' videos and images as critical
        mediaPreloader.preloadCriticalProducts(products.slice(0, 3));
        
        // Subscribe to progress updates
        const unsubscribe = mediaPreloader.onProgress((progress) => {
          setMediaProgress(progress);
          
          // Check for network issues (if nothing loaded after 5 seconds)
          if (progress.total > 0 && progress.loaded === 0 && progress.percentage === 0) {
            setTimeout(() => {
              const current = mediaPreloader.getProgress();
              if (current.loaded === 0) {
                setHasNetworkIssues(true);
              }
            }, 5000);
          }
          
          // Move to loading step when preloading starts
          if (progress.total > 0 && step === 'greeting') {
            if (hasCity) {
              setStep('loading');
            } else {
              setStep('promo');
            }
          }
          
          // Mark as ready when critical items are done (loaded or errored)
          if (progress.criticalLoaded && step !== 'ready') {
            setStep('ready');
          }
        });
        
        return unsubscribe;
      } else {
        // No products, skip to ready
        setTimeout(() => setStep('ready'), 1000);
      }
    };
    
    initPreload();
  }, [products, hasCity]);

  // Auto-complete when app is ready and media step is done
  useEffect(() => {
    if (step === 'ready' && isAppReady) {
      const timer = setTimeout(() => {
        onComplete(selectedCity || localStorage.getItem('user_city') || '');
      }, 300);
      return () => clearTimeout(timer);
    }
  }, [step, isAppReady, selectedCity, onComplete]);

  const handleCitySelect = (cityId: string) => {
    setSelectedCity(cityId);
    localStorage.setItem('user_city', cityId);
    setStep('loading');
  };

  return (
    <motion.div
      initial={{ opacity: 1 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.8, ease: [0.43, 0.13, 0.23, 0.96] }}
      className={cn(
        "fixed inset-0 z-[200] flex flex-col items-center justify-center overflow-hidden",
        theme === 'dark' ? "bg-[#141414] text-white" : "bg-[#e4e3e0] text-[#141414]"
      )}
    >
      <AnimatePresence mode="wait">
        {step === 'greeting' && (
          <motion.div
            key="greeting"
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 1.1, y: -20 }}
            transition={{ duration: 0.8, ease: "circOut" }}
            className="flex flex-col items-center gap-6"
          >
            <div className="w-24 h-24 bg-blue-600 rounded-3xl flex items-center justify-center shadow-2xl shadow-blue-600/20">
              <span className="text-5xl">🐳</span>
            </div>
            <div className="space-y-2 text-center">
              <h1 className="text-4xl font-bold tracking-tight">Привет!</h1>
              <p className="text-lg opacity-60 font-medium">Добро пожаловать в Кучу Тортиков</p>
            </div>
          </motion.div>
        )}

        {step === 'promo' && (
          <motion.div
            key="promo"
            initial={{ opacity: 0, x: 40 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -40 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="w-full max-w-sm px-8 space-y-10"
          >
            {/* Promo Card */}
            <div className="relative overflow-hidden rounded-[40px] bg-blue-600 p-8 text-white shadow-2xl shadow-blue-600/30">
              <div className="absolute -top-10 -right-10 w-40 h-40 bg-white/10 rounded-full blur-3xl" />
              <div className="relative z-10 space-y-4">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/20 text-[10px] font-bold uppercase tracking-wider">
                  <Sparkles size={12} />
                  Акция дня
                </div>
                <h2 className="text-3xl font-bold leading-tight">Скидка 20% на первый заказ</h2>
                <p className="text-sm opacity-80 leading-relaxed">
                  Закажите любимые десерты сегодня и получите специальный бонус от нашего шеф-кондитера.
                </p>
              </div>
            </div>

            {/* City Selection */}
            <div className="space-y-6">
              <div className="flex items-center gap-3 px-2">
                <div className="w-8 h-8 rounded-full bg-blue-600/10 flex items-center justify-center text-blue-600">
                  <MapPin size={18} />
                </div>
                <h3 className="text-xl font-bold">Выберите ваш город</h3>
              </div>

              <div className="grid grid-cols-1 gap-3">
                {CITIES.map((city) => (
                  <button
                    key={city.id}
                    onClick={() => handleCitySelect(city.id)}
                    className={cn(
                      "group flex items-center justify-between p-5 rounded-3xl border transition-all duration-300 active:scale-[0.98]",
                      selectedCity === city.id
                        ? "bg-blue-600 border-blue-600 text-white shadow-xl shadow-blue-600/20"
                        : theme === 'dark'
                          ? "bg-white/5 border-white/10 hover:border-white/30"
                          : "bg-white border-black/5 hover:border-black/20 shadow-sm"
                    )}
                  >
                    <span className="font-semibold">{city.name}</span>
                    <ChevronRight
                      size={18}
                      className={cn(
                        "transition-transform duration-300",
                        selectedCity === city.id ? "translate-x-0 opacity-100" : "translate-x-[-10px] opacity-0 group-hover:translate-x-0 group-hover:opacity-100"
                      )}
                    />
                  </button>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {step === 'loading' && (
          <motion.div
            key="loading"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center gap-6"
          >
            {hasNetworkIssues ? (
              <>
                <div className="w-16 h-16 bg-orange-500/20 rounded-full flex items-center justify-center">
                  <WifiOff size={32} className="text-orange-500" />
                </div>
                <div className="text-center space-y-1">
                  <p className="text-lg font-medium">Проблемы с соединением...</p>
                  <p className="text-sm opacity-60">Загружаем в фоновом режиме</p>
                </div>
              </>
            ) : (
              <>
                <div className="w-16 h-16 border-4 border-blue-600/20 border-t-blue-600 rounded-full animate-spin" />
                <p className="text-lg font-medium opacity-60">Подготовка меню...</p>
              </>
            )}
            
            {/* Progress indicator */}
            <div className="w-48 space-y-2">
              <div className="flex items-center justify-between text-xs opacity-60">
                <span>{hasNetworkIssues ? 'Загрузка...' : 'Загрузка видео...'}</span>
                <span>{mediaProgress.percentage}%</span>
              </div>
              <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${mediaProgress.percentage}%` }}
                  transition={{ duration: 0.3 }}
                  className={cn(
                    "h-full rounded-full",
                    hasNetworkIssues ? "bg-orange-500" : "bg-blue-600"
                  )}
                />
              </div>
            </div>
          </motion.div>
        )}

        {step === 'ready' && (
          <motion.div
            key="ready"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center gap-6"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 500, damping: 25 }}
              className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center"
            >
              <CheckCircle2 size={32} className="text-white" />
            </motion.div>
            <p className="text-lg font-medium opacity-60">Готово!</p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Progress Indicator */}
      {(step === 'greeting' || step === 'promo') && (
        <div className="fixed bottom-12 left-1/2 -translate-x-1/2 flex gap-2">
          <div className={cn(
            "h-1.5 rounded-full transition-all duration-500",
            step === 'greeting' ? "w-8 bg-blue-600" : "w-1.5 bg-blue-600/20"
          )} />
          <div className={cn(
            "h-1.5 rounded-full transition-all duration-500",
            step === 'promo' ? "w-8 bg-blue-600" : "w-1.5 bg-blue-600/20"
          )} />
        </div>
      )}
    </motion.div>
  );
}
