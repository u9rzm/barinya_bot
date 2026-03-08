import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import {defineConfig, loadEnv} from 'vite';
import { visualizer } from 'rollup-plugin-visualizer';

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [
    react(),
    tailwindcss(),
    // Bundle analysis - generates stats.html when building
    visualizer({
      filename: 'dist/stats.html',
      open: false,
      gzipSize: true,
      brotliSize: true,
      template: 'treemap', // sunburst, treemap, network
    }),
  ],
  base: './',
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  publicDir: './public',
  server: {
    // Exposes your dev server and makes it accessible for the devices in the same network.
    host: true,
  },
  build: {
    // Code splitting optimization
    rollupOptions: {
      output: {
        manualChunks: {
          // React and ReactDOM in their own chunk
          'react-vendor': ['react', 'react-dom'],
          // Motion - tree-shaken imports
          'motion-vendor': ['motion/react'],
          // TMA SDK in separate chunk
          'tma-sdk': ['@tma.js/sdk'],
          // HLS.js - now loaded dynamically, but keep chunk for caching
          'hls-vendor': ['hls.js'],
          // Crypto for secure storage
          'crypto-vendor': ['crypto-js'],
          // UI libraries
          'ui-vendor': ['lucide-react', 'clsx', 'tailwind-merge'],
          // Web Vitals - separate chunk for analytics
          'web-vitals': ['web-vitals'],
          // Virtualization - separate chunk
          'virtual': ['@tanstack/react-virtual'],
        },
        // Improve chunk naming for better debugging
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]',
      },
    },
    // Chunk size warning limit
    chunkSizeWarningLimit: 500,
    // Enable minification for better compression
    minify: 'esbuild',
    // Use esbuild for faster transpilation
    target: 'esnext',
    // Enable tree-shaking
    treeShaking: true,
    // Generate sourcemaps for production debugging
    sourcemap: mode === 'production',
  },
  // Optimize dependencies pre-bundling
  optimizeDeps: {
    include: ['react', 'react-dom'],
    // Exclude large libraries from pre-bundling
    exclude: ['motion/react', '@tanstack/react-virtual'],
  },
}));
