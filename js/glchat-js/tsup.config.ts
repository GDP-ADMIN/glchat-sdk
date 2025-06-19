import { defineConfig } from 'tsup';

import packageDef from './package.json';

export default defineConfig({
  entry: ['src/index.ts'],
  minify: 'terser',
  format: ['cjs', 'esm'],
  clean: true,
  sourcemap: true,
  dts: true,
  define: {
    __packageVersion: JSON.stringify(packageDef.version),
  },
});
