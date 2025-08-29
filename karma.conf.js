/* eslint-env node */

const webpack = require('webpack');
const webpackConfig = require('./webpack.config.js');

module.exports = function(config) {
    // set timezone for tests
    process.env.TZ = 'Europe/Prague';

    config.set({
        files: [
            // Load a simple video.js mock before tests
            {pattern: 'node_modules/video.js/dist/video.js', included: true, served: true},
            'assets/tests.ts',
        ],

        preprocessors: {
            'assets/tests.ts': ['webpack', 'sourcemap'],
        },

        webpack: {
            module: webpackConfig.module,
            resolve: webpackConfig.resolve,
            devtool: 'inline-source-map',
            mode: 'development',
            externals: {
                'video.js': 'videojs',
            },
        },

        webpackMiddleware: {
            stats: 'errors-only'
        },

        reporters: ['dots'],
        frameworks: ['jasmine', 'webpack'],
        browsers: ['ChromeHeadless'],

        // Allow typescript files
        mime: {
            'text/x-typescript': ['ts', 'tsx'],
        },
    });
};
