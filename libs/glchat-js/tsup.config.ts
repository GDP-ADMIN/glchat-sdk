import { defineConfig } from 'tsup';

import packageDef from './package.json';

export default defineConfig({
  entry: ['src/index.ts'],
  minify: 'terser',
  define: {
    __packageVersion: packageDef.version,
  },
});
