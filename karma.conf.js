/* eslint-env node */

import {ProvidePlugin} from 'webpack';
import {module as _module, resolve as _resolve, plugins as _plugins} from './webpack.config.js';

export default function(config) {
    config.set({
        files: [
            'assets/tests.js',
        ],

        preprocessors: {
            'assets/tests.js': ['webpack', 'sourcemap'],
        },

        webpack: {
            module: _module,
            resolve: _resolve,
            plugins: _plugins.filter((plugin) => plugin instanceof ProvidePlugin),
            devtool: 'inline-source-map',
        },

        webpackMiddleware: {
            stats: 'errors-only'
        },

        reporters: ['dots'],
        frameworks: ['jasmine'],
        browsers: ['ChromeHeadless'],
    });
}
