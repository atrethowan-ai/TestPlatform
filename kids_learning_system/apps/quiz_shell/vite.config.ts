import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
  root: '.',
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@shared_types': path.resolve(__dirname, '../../packages/shared_types'),
      '@quiz_domain': path.resolve(__dirname, '../../packages/quiz_domain/src'),
      '@storage_indexeddb': path.resolve(__dirname, '../../packages/storage_indexeddb/src'),
    },
  },
});