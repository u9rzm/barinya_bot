import { Product } from '../constants/types';

export interface UserAction {
  productId: string;
  timestamp: number;
  type: 'view' | 'purchase';
}

export interface UserProfile {
  history: UserAction[];
  preferences: Record<string, number>; // categoryId -> weight
}

/**
 * Сервис рекомендаций на основе весовых коэффициентов (без LLM).
 * Использует историю покупок и просмотров для ранжирования каталога.
 */
class RecommendationService {
  private readonly PURCHASE_WEIGHT = 5;
  private readonly VIEW_WEIGHT = 1;
  private readonly NOVELTY_BOOST = 1.5;
  private readonly RANDOM_FACTOR = 0.5;

  /**
   * Детерминированный "рандом" на основе productId (для стабильной сортировки)
   * Возвращает значение от 0 до 1 на основе хэша строки
   */
  private deterministicRandom(productId: string): number {
    let hash = 0;
    for (let i = 0; i < productId.length; i++) {
      const char = productId.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    // Нормализуем до [0, 1]
    return Math.abs(hash) / 2147483647;
  }

  /**
   * Рассчитывает профиль предпочтений пользователя на основе истории
   */
  getUserProfile(history: UserAction[], products: Product[]): UserProfile {
    const preferences: Record<string, number> = {};

    history.forEach(action => {
      const product = products.find(p => p.id === action.productId);
      if (!product) return;

      const weight = action.type === 'purchase' ? this.PURCHASE_WEIGHT : this.VIEW_WEIGHT;
      preferences[product.category] = (preferences[product.category] || 0) + weight;
    });

    return { history, preferences };
  }

  /**
   * Сортирует продукты для конкретного пользователя
   */
  getRecommendedProducts(products: Product[], profile: UserProfile | null, filterUntried = false): Product[] {
    if (!profile) {
      // Если нет профиля, возвращаем продукты как есть или сортируем по популярности
      return filterUntried ? products : [...products];
    }

    const boughtIds = new Set(
      profile.history
        .filter(a => a.type === 'purchase')
        .map(a => a.productId)
    );

    return [...products].sort((a, b) => {
      const scoreA = this.calculateScore(a, profile, boughtIds, filterUntried);
      const scoreB = this.calculateScore(b, profile, boughtIds, filterUntried);
      return scoreB - scoreA;
    });
  }

  private calculateScore(product: Product, profile: UserProfile, boughtIds: Set<string>, filterUntried: boolean): number {
    let score = 0;

    // 1. Глобальная популярность (базовый вес от сервера)
    score += (product.popularity || 0) * 0.5;

    // 2. Базовый вес от категории (предпочтения пользователя)
    const categoryWeight = profile.preferences[product.category] || 0;
    score += categoryWeight;

    // 3. Буст для новинок (то, что не пробовал)
    const hasTried = boughtIds.has(product.id);
    if (!hasTried) {
      score *= this.NOVELTY_BOOST;
    }

    // 4. Если мы специально ищем "Новинки", и пользователь это уже пробовал - сильно снижаем приоритет
    if (filterUntried && hasTried) {
      score -= 1000;
    }

    // 5. Детерминированный "рандом" для вариативности (стабильная сортировка)
    score += this.deterministicRandom(product.id) * this.RANDOM_FACTOR;

    return score;
  }
}

export const recommendationService = new RecommendationService();
