import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: resolve(__dirname, 'render.html'),
      output: { entryFileNames: 'assets/render-[hash].js' },
    },
  },
});
