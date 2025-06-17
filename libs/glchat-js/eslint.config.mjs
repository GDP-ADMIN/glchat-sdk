// @ts-check

import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';

import stylistic from '@stylistic/eslint-plugin';

export default tseslint.config(
  eslint.configs.recommended,
  tseslint.configs.strictTypeChecked,
  {
    languageOptions: {
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.url,
      },
    },
  },
  stylistic.configs.customize({
    indent: 2,
    quotes: 'single',
    semi: true,
    braceStyle: '1tbs',
    quoteProps: 'consistent-as-needed',
    commaDangle: 'always-multiline',
  }),
  tseslint.configs.stylisticTypeChecked,
);
