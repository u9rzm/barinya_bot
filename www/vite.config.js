import { defineConfig } from 'vite'
import { resolve } from 'path'

export default defineConfig({
  root: '.',                // важно
  publicDir: 'public', 
  
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
      },
    },
  },
  server: {
    // Exposes your dev server and makes it accessible for the devices in the same network.
    host: true,}
})
