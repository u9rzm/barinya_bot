/**
 * Throttle function - ensures a function is called at most once in a specified time interval.
 * 
 * @param func - The function to throttle
 * @param limit - The minimum time between function invocations
 * @returns A throttled version of the function
 * 
 * @example
 * // Usage for scroll events:
 * const throttledScroll = throttle(() => {
 *   // Handle scroll
 * }, 100);
 * 
 * // Will execute at most once every 100ms
 * window.addEventListener('scroll', throttledScroll);
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean = false;
  let lastFunc: ReturnType<typeof setTimeout> | null = null;
  let lastArgs: Parameters<T> | null = null;

  return function executedFunction(...args: Parameters<T>) {
    if (inThrottle) {
      // If we're in throttle period, save the last args
      lastArgs = args;
      if (!lastFunc) {
        // Schedule execution at the end of throttle period
        lastFunc = setTimeout(() => {
          if (lastArgs) {
            func(...lastArgs);
          }
          lastFunc = null;
          lastArgs = null;
        }, limit);
      }
      return;
    }

    // Execute immediately
    func(...args);
    inThrottle = true;

    // Reset throttle after limit
    setTimeout(() => {
      inThrottle = false;
    }, limit);
  };
}

/**
 * Throttle with leading and trailing options
 * 
 * @param func - The function to throttle
 * @param wait - The number of milliseconds to delay
 * @param options - Configuration object
 * @param options.leading - Invoke on the leading edge of the timeout
 * @param options.trailing - Invoke on the trailing edge of the timeout
 * @returns A throttled version of the function
 * 
 * @example
 * // Leading edge only (first call executes, rest are ignored)
 * const throttledClick = throttle(handleClick, 1000, { leading: true, trailing: false });
 * 
 * // Trailing edge only (first call is delayed, last call executes)
 * const throttledResize = throttle(handleResize, 200, { leading: false, trailing: true });
 */
export function throttleWithOptions<T extends (...args: any[]) => any>(
  func: T,
  wait: number,
  options: { leading?: boolean; trailing?: boolean } = {}
): (...args: Parameters<T>) => void {
  const { leading = true, trailing = true } = options;
  
  let timeout: ReturnType<typeof setTimeout> | null = null;
  let previous = 0;
  let lastArgs: Parameters<T> | null = null;

  const later = () => {
    previous = leading === false ? 0 : Date.now();
    timeout = null;
    if (lastArgs) {
      func(...lastArgs);
      lastArgs = null;
    }
  };

  return function throttledFunction(...args: Parameters<T>) {
    const now = Date.now();
    
    if (!previous && leading === false) {
      previous = now;
    }

    const remaining = wait - (now - previous);

    if (remaining <= 0 || remaining > wait) {
      if (timeout) {
        clearTimeout(timeout);
        timeout = null;
      }
      previous = now;
      func(...args);
    } else if (!timeout && trailing !== false) {
      lastArgs = args;
      timeout = setTimeout(later, remaining);
    }
  };
}
