/**
 * Debounce function - delays function execution until after a specified wait time
 * has elapsed since the last time the function was invoked.
 * 
 * @param func - The function to debounce
 * @param wait - The number of milliseconds to delay
 * @returns A debounced version of the function
 * 
 * @example
 * // Usage in a component:
 * const debouncedSearch = debounce((query) => {
 *   // Search logic here
 * }, 300);
 * 
 * // Call it multiple times, but it will only execute once after 300ms of no calls
 * debouncedSearch('test');
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null;

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      func(...args);
    };

    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(later, wait);
  };
}

/**
 * Debounce with immediate execution on first call
 * Useful for actions that should happen immediately but then rate-limited
 * 
 * @param func - The function to debounce
 * @param wait - The number of milliseconds to delay
 * @param immediate - If true, triggers on leading edge instead of trailing
 * @returns A debounced version of the function
 * 
 * @example
 * // Immediate execution, then rate-limited
 * const debouncedClick = debounce(handleClick, 1000, true);
 */
export function debounceWithImmediate<T extends (...args: any[]) => any>(
  func: T,
  wait: number,
  immediate?: boolean
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null;
  let result: ReturnType<T> | undefined;

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      if (!immediate) {
        result = func(...args);
      }
    };

    const callNow = immediate && !timeout;
    
    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(later, wait);

    if (callNow) {
      result = func(...args);
    }

    return result;
  };
}
