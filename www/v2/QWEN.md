# Gourmet Delivery App - Project Context

## Project Overview

A premium food and beverage delivery application built as a **Telegram Mini App (TMA)** with AI-powered product recommendations. The app features a high-end UI/UX with video backgrounds, product customization, and a sophisticated recommendation system.

**Key Features:**
- Telegram Mini App integration with full-screen viewport and swipe gestures
- Video-backed product cards with smooth swipe navigation between categories
- Product customization (milk types, syrups, toppings) with conditional free thresholds
- AI-based recommendation engine using weighted user preferences (views + purchases)
- Dark/Light theme support
- Cart management with localStorage persistence
- Checkout flow with multiple payment methods

## Tech Stack

| Category | Technology |
|----------|------------|
| **Framework** | React 19 with TypeScript |
| **Build Tool** | Vite 6 |
| **Styling** | Tailwind CSS 4, shadcn/ui (new-york style) |
| **Animations** | Motion (motion/react) |
| **State** | React useState/useEffect, localStorage persistence |
| **UI Components** | Radix UI, Lucide React icons |
| **TMA SDK** | @tma.js/sdk for Telegram integration |
| **Video** | HLS.js for adaptive video streaming |

## Project Structure

```
www/v2/
├── src/
│   ├── App.tsx              # Main component: state management, navigation, data loading
│   ├── main.tsx             # Entry point with error boundary
│   ├── constants.ts         # TypeScript interfaces (Product, Category, CartItem, etc.)
│   ├── index.css            # Global styles + Tailwind
│   ├── components/
│   │   ├── MainPage.tsx     # Hero section with swipeable video cards
│   │   ├── ProductDetail.tsx # Product modal with customization
│   │   ├── CatalogSheet.tsx # Full product catalog view
│   │   ├── CartSheet.tsx    # Shopping cart drawer
│   │   ├── CheckoutSheet.tsx # Checkout flow
│   │   ├── LoadingScreen.tsx # Onboarding + loading states
│   │   ├── OptimizedVideo.tsx # HLS video component
│   │   └── UI.tsx           # Reusable UI components
│   ├── services/
│   │   └── recommendationService.ts # User preference-based ranking algorithm
│   └── utils/
│       └── cn.ts            # className merger utility
├── public/
│   ├── data.json            # Menu data (categories, products, addons, options)
│   └── stock.json           # Stock availability data
├── package.json             # Dependencies and scripts
├── tsconfig.json            # TypeScript config (paths: @/* → src/*)
├── vite.config.ts           # Vite config with React + Tailwind plugins
├── components.json          # shadcn/ui configuration
└── analyze_bundle.py        # Bundle size analysis script
```

## Building and Running

### Prerequisites
- Node.js (v18+)
- Gemini API key (for AI features, configured via `.env.local`)

### Commands

```bash
# Install dependencies
npm install

# Start development server (port 3000, accessible on local network)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type check
npm run lint

# Clean build artifacts
npm run clean
```

### Environment Variables

Create `.env.local` based on `.env.example`:

```bash
GEMINI_API_KEY="your_gemini_api_key"
APP_URL="https://your-app-url.com"
```

## Development Conventions

### Code Style
- **TypeScript**: Strict mode with `noEmit` for type checking
- **Component naming**: PascalCase for components, camelCase for utilities
- **File naming**: PascalCase for React components (`.tsx`), camelCase for utilities (`.ts`)
- **Imports**: Use `@/` alias for `src/` directory

### Architecture Patterns
- **State management**: Local React state + localStorage persistence
- **Data flow**: Products loaded from `data.json` with 60-second polling interval
- **Recommendation engine**: Weighted scoring system (Purchase: 5pts, View: 1pt, Novelty boost: 1.5x)
- **Error handling**: Global error boundary in `main.tsx` displays runtime errors on screen

### Key Implementation Details

1. **Product Addons System**: 
   - Addons resolved via `addonGroups` → `addons` → `options` relationship
   - Support for `single`, `multiple`, and `toggle` selection types
   - Conditional free thresholds (e.g., free syrup for orders >300₽)

2. **Telegram Mini App Integration**:
   - Auto-expands to fullscreen viewport
   - Disabled vertical swipe for better UX
   - Receives `initData` from Telegram for user authentication

3. **Video Optimization**:
   - HLS streaming with adaptive quality
   - Lazy loading with `OptimizedVideo` component
   - Loading states tracked per product

4. **Cart Logic**:
   - Items differentiated by selected options
   - Quantity updates with zero-removal
   - Persistent across sessions via localStorage

## Data Model

### Product Structure
```typescript
interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  image: string;
  videoUrl?: string;
  category: string;
  addons?: Addon[];
  popularity?: number; // 0-100 server-provided rating
  // ... nutrition info
}
```

### Recommendation Algorithm
The `recommendationService` ranks products using:
1. Global popularity score (50% weight)
2. User category preferences (based on history)
3. Novelty boost for untried products (1.5x multiplier)
4. Random factor for variety (0-0.5)

## External Resources

- **AI Studio App**: https://ai.studio/apps/c237fcfa-1f0d-4a63-b9cc-4bead8a02
- **shadcn/ui**: https://ui.shadcn.com/docs
- **Telegram Mini Apps**: https://core.telegram.org/bots/webapps
- **Motion**: https://motion.dev/docs
