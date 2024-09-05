/* eslint-env node */

const webpack = require('webpack');
const webpackConfig = require('./webpack.config.js');

module.exports = function(config) {
    // set timezone for tests
    process.env.TZ = 'Europe/Prague';

    config.set({
        files: [
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
