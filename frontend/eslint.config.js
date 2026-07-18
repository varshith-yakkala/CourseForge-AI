import js from '@eslint/js'
import reactPlugin from 'eslint-plugin-react'
import reactHooksPlugin from 'eslint-plugin-react-hooks'
import reactRefreshPlugin from 'eslint-plugin-react-refresh'

/** @type {import('eslint').Linter.Config[]} */
export default [
  // Base JS rules
  js.configs.recommended,

  // React rules
  {
    plugins: {
      react: reactPlugin,
      'react-hooks': reactHooksPlugin,
      'react-refresh': reactRefreshPlugin,
    },
    settings: {
      react: {
        version: 'detect',
      },
    },
    rules: {
      // React
      ...reactPlugin.configs.recommended.rules,
      'react/react-in-jsx-scope': 'off',       // Not needed in React 17+
      'react/prop-types': 'off',               // Using JSDoc instead of PropTypes
      'react/display-name': 'warn',

      // React Hooks
      ...reactHooksPlugin.configs.recommended.rules,

      // React Refresh (HMR)
      'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],

      // General
      'no-console': ['warn', { allow: ['warn', 'error'] }],
      'no-unused-vars': ['warn', { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }],
      'prefer-const': 'error',
      'no-var': 'error',
    },
  },

  // Test files — relax rules
  {
    files: ['src/test/**', '**/*.test.{js,jsx}'],
    rules: {
      'no-console': 'off',
    },
  },

  // Ignore patterns
  {
    ignores: ['dist/', 'node_modules/', 'coverage/', '*.config.js'],
  },
]
