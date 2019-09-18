module.exports = {
  "parser": "babel-eslint",
  "env": {
    "browser": true,
    "es6": true,
    "jest": true,
    "node": true
  },
  parserOptions:  {
    ecmaVersion: 2018,
    sourceType: 'module',
  },
  'plugins': [
    'react',
    'react-app',
    'prettier',
    'jest',
    'compat',
    'extra-rules',
  ],
  "settings": {
    "polyfills": [
      "fetch",
      "promises"
    ]
  },
  extends: [
    'airbnb',
    'prettier',
    'plugin:prettier/recommended',
  ],
  "rules": {
    "react/prop-types": "off",
    "linebreak-style": "off",
  },
  'env': {
    'jest/globals': true,
    browser: true,
    node: true,
  },
  'rules': {
    'prettier/prettier': ['error'],
    'linebreak-style': 'off',
    'react/prop-types': 'off',
    'jsx-a11y/href-no-hash': 'off',
    'react/jsx-one-expression-per-line': 'off' // Conflicts with Prettier
  },
  settings: {
    react:  {
      version:  'detect',
    },
  },
}
