export interface AddonOption {
  id: string;
  name: string;
  image: string;
  price?: number;
  freeThreshold?: number;
  selectionType?: 'single' | 'toggle' | 'multiple';
}

export interface Addon {
  id: string;
  name: string;
  options: AddonOption[];
  optionIds?: string[]; // Used in raw data
}

export interface AppData {
  categories: Category[];
  options: Record<string, AddonOption>;
  addons: Record<string, {
    id: string;
    name: string;
    optionIds: string[];
  }>;
  addonGroups: Record<string, string[]>;
  products: Product[];
}

export interface Product {
  id: string;
  name: string;
  description: string;
  longDescription?: string;
  price: number;
  image: string;
  videoUrl?: string;
  calories: number;
  proteins: number;
  fats: number;
  carbs: number;
  category: string;
  subcategory?: string;
  volume: string;
  label?: string;
  labelColor?: string;
  addons?: Addon[];
  popularity?: number; // Глобальный рейтинг популярности от сервера (0-100)
}

export interface Category {
  id: string;
  name: string;
}

export interface CartItem {
  product: Product;
  quantity: number;
  selectedOptions: AddonOption[];
}

export interface User {
  name: string;
  avatar: string;
  id?: number;
  username?: string;
  preferredPaymentMethod?: 'delivery' | 'card' | 'crypto';
  savedCards?: { id: string; last4: string; brand: string }[];
  cryptoAddress?: string;
}

// Data will be fetched from data.json
export const CATEGORIES: Category[] = [];
export const PRODUCTS: Product[] = [];