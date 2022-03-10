/* eslint-env node */

const path = require('path');
const webpack = require('webpack');
const ManifestPlugin = require('webpack-manifest-plugin');
const TerserPlugin = require('terser-webpack-plugin-legacy');

const config = {
    entry: {
        newsroom_js: path.resolve(__dirname, 'assets/index.js'),
        companies_js: path.resolve(__dirname, 'assets/companies/index.js'),
        oauth_clients_js: path.resolve(__dirname, 'assets/oauth_clients/index.js'),
        users_js: path.resolve(__dirname, 'assets/users/index.js'),
        products_js: path.resolve(__dirname, 'assets/products/index.js'),
        'section-filters_js': path.resolve(__dirname, 'assets/section-filters/index.js'),
        navigations_js: path.resolve(__dirname, 'assets/navigations/index.js'),
        cards_js: path.resolve(__dirname, 'assets/cards/index.js'),
        user_profile_js: path.resolve(__dirname, 'assets/user-profile/index.js'),
        newsroom_css: path.resolve(__dirname, 'assets/style.js'),
        wire_js: path.resolve(__dirname, 'assets/wire/index.js'),
        home_js: path.resolve(__dirname, 'assets/home/index.js'),
        agenda_js: path.resolve(__dirname, 'assets/agenda/index.js'),
        notifications_js: path.resolve(__dirname, 'assets/notifications/index.js'),
        company_reports_js: path.resolve(__dirname, 'assets/company-reports/index.js'),
        print_reports_js: path.resolve(__dirname, 'assets/company-reports/components/index.js'),
        am_news_js: path.resolve(__dirname, 'assets/am-news/index.js'),
        am_news_css: path.resolve(__dirname, 'assets/am-news/style.js'),
        'general-settings_js': path.resolve(__dirname, 'assets/general-settings/index.js'),
        market_place_js: path.resolve(__dirname, 'assets/market-place/index.js'),
        media_releases_js: path.resolve(__dirname, 'assets/media-releases/index.js'),
        monitoring_js: path.resolve(__dirname, 'assets/monitoring/index.js'),
        factcheck_js: path.resolve(__dirname, 'assets/factcheck/index.js'),
        common: path.resolve(__dirname, 'assets/common.js'),
    },
    output: {
        path: path.resolve(process.cwd(), 'dist'),
        publicPath: 'http://localhost:8080/',
        filename: '[name].[chunkhash].js',
        chunkFilename: '[id].[chunkhash].js'
    },
    module: {
        rules: [
            {
                test: /\.jsx?$/,
                include: path.resolve(__dirname, 'assets'),
                loader: 'babel-loader',
                options: {
                    presets: ['es2015', 'react'],
                    plugins: ['transform-object-rest-spread'],
                }
            },
            {
                test: /\.css$/,
                use: [
                    'style-loader',
                    'css-loader',
                ],
            },
            {
                test: /\.scss$/,
                use: [
                    'style-loader',
                    'css-loader',
                    'sass-loader',
                ],
            },
        ]
    },
    resolve: {
        extensions: ['.js', '.jsx'],
        modules: [
            path.resolve(__dirname, 'assets'),
            'node_modules',
        ],
    },
    plugins: [
        new ManifestPlugin(),
        new webpack.ProvidePlugin({
            $: 'jquery',
            // bootstrap depenendecies
            'window.jQuery': 'jquery',
            'window.Popper': 'popper.js',
        }),
        new webpack.optimize.CommonsChunkPlugin({
            name: 'common',
            minChunks: Infinity,
        }),
    ],
    devServer: {
        compress: true,
        disableHostCheck: true,
    },
};

if (process.env.NODE_ENV === 'production') {
    console.log('PRODUCTION MODE');
    config.plugins.push(new webpack.DefinePlugin({
        'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV)
    }));
    config.plugins.push(new TerserPlugin({
        cache: true,
        parallel: true,
    }));
} else {
    console.log('DEVELOPMENT MODE');
}

module.exports = config;
