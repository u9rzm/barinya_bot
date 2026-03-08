import {StrictMode} from 'react';
import {createRoot} from 'react-dom/client';
import {ErrorBoundary} from './components/ErrorBoundary';
import {AuthProvider} from './auth';
import App from './App.tsx';
import './index.css';
import { webVitals } from './services/webVitals';

// Debug: Display runtime errors on screen
window.onerror = (message, source, lineno, colno, error) => {
  console.error('Global error:', message, source, lineno, colno, error);
};

// Initialize Web Vitals monitoring in development
if (import.meta.env.DEV) {
  webVitals.init();
  console.log('[WebVitals] Monitoring enabled (dev only)');
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider>
      <ErrorBoundary>
        <App />
      </ErrorBoundary>
    </AuthProvider>
  </StrictMode>,
);
