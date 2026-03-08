/**
 * UI Constants
 * Centralized constants for consistent UI values across the application.
 */

// ==================== Animation Values ====================

/**
 * Animation timing values (in milliseconds)
 */
export const ANIMATION = {
  /** Default transition duration */
  DURATION_DEFAULT: 300,
  /** Slow transition for complex animations */
  DURATION_SLOW: 500,
  /** Fast transition for micro-interactions */
  DURATION_FAST: 150,
  /** Spring damping factor */
  SPRING_DAMPING: 25,
  /** Spring stiffness factor */
  SPRING_STIFFNESS: 200,
} as const;

/**
 * Drag and swipe thresholds
 */
export const DRAG = {
  /** Minimum drag distance to trigger action (pixels) */
  THRESHOLD_MIN: 80,
  /** Swipe velocity threshold */
  VELOCITY_THRESHOLD: 300,
  /** Drag elastic resistance (0-1) */
  ELASTIC: 0.1,
  /** Category swipe threshold (fraction of screen) */
  CATEGORY_THRESHOLD: 0.15,
} as const;

// ==================== Layout Values ====================

/**
 * Border radius values (in pixels)
 */
export const RADIUS = {
  /** Small radius for buttons and inputs */
  SMALL: 16,
  /** Medium radius for cards */
  MEDIUM: 24,
  /** Large radius for sheets and modals */
  LARGE: 32,
  /** Full radius for circular elements */
  FULL: 9999,
} as const;

/**
 * Spacing values (in pixels)
 */
export const SPACING = {
  /** Extra small gap */
  XS: 4,
  /** Small gap */
  SM: 8,
  /** Medium gap */
  MD: 16,
  /** Large gap */
  LG: 24,
  /** Extra large gap */
  XL: 32,
} as const;

/**
 * Z-index layers for consistent stacking
 */
export const Z_INDEX = {
  /** Base layer */
  BASE: 0,
  /** Dropdowns and tooltips */
  DROPDOWN: 10,
  /** Sticky headers */
  STICKY: 20,
  /** Fixed elements */
  FIXED: 30,
  /** Modal overlays */
  MODAL: 40,
  /** Toast notifications */
  TOAST: 50,
  /** Loading spinners */
  LOADING: 60,
} as const;

// ==================== Timing Values ====================

/**
 * Debounce and throttle delays (in milliseconds)
 */
export const TIMING = {
  /** Standard debounce delay */
  DEBOUNCE_DEFAULT: 300,
  /** Fast debounce for typing */
  DEBOUNCE_FAST: 150,
  /** Slow debounce for search */
  DEBOUNCE_SLOW: 500,
  /** Standard throttle delay */
  THROTTLE_DEFAULT: 300,
  /** Fast throttle for scroll */
  THROTTLE_SCROLL: 100,
  /** Polling interval for data refresh */
  POLLING_INTERVAL: 60000,
} as const;

/**
 * Loading and timeout values (in milliseconds)
 */
export const LOADING = {
  /** Minimum loading time for smooth UX */
  MINIMUM_DISPLAY: 500,
  /** Stock verification timeout */
  VERIFY_TIMEOUT: 1200,
  /** Order confirmation delay */
  CONFIRM_DELAY: 1500,
  /** Retry delay on failure */
  RETRY_DELAY: 2000,
} as const;

// ==================== Component-Specific Values ====================

/**
 * Catalog sheet values
 */
export const CATALOG = {
  /** Initial delay before centering category */
  CENTER_DELAY: 50,
  /** Grid columns for product display */
  GRID_COLUMNS: 2,
  /** Product card aspect ratio */
  ASPECT_RATIO: '3/4',
} as const;

/**
 * Video player values
 */
export const VIDEO = {
  /** Fade transition duration */
  FADE_DURATION: 400,
  /** Loop fade start time (seconds before end) */
  LOOP_FADE_START: 0.4,
  /** Loading margin (pixels before viewport) */
  LAZY_MARGIN: 50,
} as const;

/**
 * Cart values
 */
export const CART = {
  /** Cart sheet border radius */
  BORDER_RADIUS: 40,
  /** Maximum cart height (viewport units) */
  MAX_HEIGHT: 90,
  /** Item image size */
  IMAGE_SIZE: 80,
} as const;

/**
 * Product detail values
 */
export const PRODUCT = {
  /** Description modal width */
  DESCRIPTION_WIDTH: '85%',
  /** Addon menu max height */
  ADDON_MENU_HEIGHT: '60vh',
  /** Quantity button size */
  BUTTON_SIZE: 32,
} as const;

// ==================== Thresholds ====================

/**
 * Scroll and visibility thresholds
 */
export const THRESHOLDS = {
  /** Scroll position to trigger actions */
  SCROLL_ACTION: 100,
  /** Opacity transition start */
  OPACITY_START: 0,
  /** Opacity transition end */
  OPACITY_END: 300,
  /** Description modal drag threshold */
  MODAL_DRAG_THRESHOLD: 50,
  /** Product detail drag threshold */
  DETAIL_DRAG_THRESHOLD: 150,
} as const;

// ==================== Export All ====================

/**
 * All UI constants grouped together
 */
export const UI = {
  ANIMATION,
  DRAG,
  RADIUS,
  SPACING,
  Z_INDEX,
  TIMING,
  LOADING,
  CATALOG,
  VIDEO,
  CART,
  PRODUCT,
  THRESHOLDS,
} as const;
