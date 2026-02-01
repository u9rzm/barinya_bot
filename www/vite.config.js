import { defineConfig } from 'vite'
import { resolve } from 'path'

export default defineConfig({
  root: '.',                // важно
  publicDir: 'public', 
//   base: 'https://c593727ccf.tapps.global/dev',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
      },
    },
  },
})
