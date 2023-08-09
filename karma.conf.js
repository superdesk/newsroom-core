/* eslint-env node */

const webpack = require('webpack');
const webpackConfig = require('./webpack.config.js');

module.exports = function(config) {
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
            plugins: webpackConfig.plugins.filter((plugin) => plugin instanceof webpack.ProvidePlugin),
            devtool: 'inline-source-map',
        },

        webpackMiddleware: {
            stats: 'errors-only'
        },

        reporters: ['dots'],
        frameworks: ['jasmine'],
        browsers: ['ChromeHeadless'],

        // Allow typescript files
        mime: {
            'text/x-typescript': ['ts', 'tsx'],
        },
    });
};
