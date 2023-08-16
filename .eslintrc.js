module.exports = {
    'env': {
        'browser': true,
        'es6': true,
        'jasmine': true
    },
    'globals': {
        '$': true,
        'sectionNames': 'readonly',
    },
    'extends': ['eslint:recommended', 'plugin:react/recommended', 'plugin:@typescript-eslint/recommended'],
    'parser': '@typescript-eslint/parser',
    'parserOptions': {
        'ecmaFeatures': {
            'experimentalObjectRestSpread': true,
            'jsx': true
        },
        'sourceType': 'module'
    },
    'plugins': [
        'react',
        '@typescript-eslint',
    ],
    'rules': {
        '@typescript-eslint/no-explicit-any': 0,
        'indent': [
            'error',
            4
        ],
        "@typescript-eslint/ban-types": [
            {
                '{}': false
            }
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
