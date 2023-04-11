module.exports = {
    'env': {
        'browser': true,
        'es6': true,
        'jasmine': true
    },
    'globals': {
        '$': true
    },
    'extends': ['eslint:recommended', 'plugin:react/recommended', 'plugin:@typescript-eslint/recommended'],
    'parserOptions': {
        'ecmaFeatures': {
            'experimentalObjectRestSpread': true,
            'jsx': true
        },
        'sourceType': 'module'
    },
    'parser': '@typescript-eslint/parser',
    'plugins': [
        'react',
        '@typescript-eslint',
    ],
    'rules': {
        'no-implicit-any': 0,
        'indent': [
            'error',
            4
        ],
        'linebreak-style': [
            'error',
            'unix'
        ],
        'quotes': [
            'error',
            'single'
        ],
        'semi': [
            'error',
            'always'
        ],
        'no-console': [
            'error',
            {'allow': ['warn', 'error']}
        ],
        'object-curly-spacing': ['error', 'never'],
        'react/no-deprecated': [
            1,
        ],
        'react/jsx-no-target-blank': [
            0,
        ],
        'react/display-name': [0]
    },
    'settings': {
        'react': {
            'version': '16.2'
        }
    }
};
