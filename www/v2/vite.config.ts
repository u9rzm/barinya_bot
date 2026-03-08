import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import {defineConfig, loadEnv} from 'vite';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
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
          // Motion/Framer in their own chunk (large library)
          'motion-vendor': ['motion/react'],
          // TMA SDK in separate chunk
          'tma-sdk': ['@tma.js/sdk'],
          // HLS.js - now loaded dynamically, but keep chunk for caching
          'hls-vendor': ['hls.js'],
          // Crypto for secure storage
          'crypto-vendor': ['crypto-js'],
          // UI libraries
          'ui-vendor': ['lucide-react', 'clsx', 'tailwind-merge'],
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
  },
  // Optimize dependencies pre-bundling
  optimizeDeps: {
    include: ['react', 'react-dom', 'motion/react'],
  },
})
