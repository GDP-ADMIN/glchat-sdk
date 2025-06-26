import { defineConfig } from 'vitest/config';

import { resolve } from 'node:path';

export default defineConfig({
  test: {
    setupFiles: ['vitest.setup.ts'],
    coverage: {
      include: ['src/**/*.ts'],
      exclude: ['src/index.ts'],
    },
    env: {
      GLCHAT_API_KEY: 'test-key',
    },
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
});
