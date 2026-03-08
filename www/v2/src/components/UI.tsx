import { cn } from '../utils/cn';

// Кнопка действия в круговом меню
export function CircleMenuAction({ icon, onClick, theme, danger }: any) {
  return (
    <button 
      onClick={onClick}
      className={cn(
        "w-10 h-10 rounded-full flex items-center justify-center transition-all active:scale-90 shadow-lg border border-white/20 backdrop-blur-md",
        theme === 'dark' ? "bg-[#1a1a1a]/80 text-white" : "bg-white/80 text-black",
        danger && (theme === 'dark' ? "text-red-400" : "text-red-500")
      )}
    >
      {icon}
    </button>
  );
}

// Кнопка авторизации в меню профиля
export function AuthButton({ icon, label, onClick, theme }: any) {
  return (
    <button 
      onClick={onClick}
      className={cn(
        "w-full flex items-center gap-4 p-4 rounded-2xl transition-all active:scale-[0.98]",
        theme === 'dark' ? "bg-white/5 hover:bg-white/10" : "bg-black/5 hover:bg-black/10"
      )}
    >
      <div className={cn(
        "w-10 h-10 rounded-xl flex items-center justify-center",
        theme === 'dark' ? "bg-white/10" : "bg-white shadow-sm"
      )}>
        {icon}
      </div>
      <span className="font-medium">{label}</span>
    </button>
  );
}
