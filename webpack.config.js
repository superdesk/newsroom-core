/* eslint-env node */

const path = require('path');
const webpack = require('webpack');
const ManifestPlugin = require('webpack-manifest-plugin');
const TerserPlugin = require('terser-webpack-plugin-legacy');
const ObjectRestSpreadPlugin = require('@sucrase/webpack-object-rest-spread-plugin');

const config = {
    entry: {
        newsroom_js: path.resolve(__dirname, 'assets/index.ts'),
        companies_js: path.resolve(__dirname, 'assets/companies/index.ts'),
        oauth_clients_js: path.resolve(__dirname, 'assets/oauth_clients/index.ts'),
        users_js: path.resolve(__dirname, 'assets/users/index.ts'),
        products_js: path.resolve(__dirname, 'assets/products/index.ts'),
        'section-filters_js': path.resolve(__dirname, 'assets/section-filters/index.ts'),
        navigations_js: path.resolve(__dirname, 'assets/navigations/index.ts'),
        cards_js: path.resolve(__dirname, 'assets/cards/index.ts'),
        user_profile_js: path.resolve(__dirname, 'assets/user-profile/index.ts'),
        newsroom_css: path.resolve(__dirname, 'assets/style.ts'),
        wire_js: path.resolve(__dirname, 'assets/wire/index.ts'),
        home_js: path.resolve(__dirname, 'assets/home/index.ts'),
        agenda_js: path.resolve(__dirname, 'assets/agenda/index.ts'),
        notifications_js: path.resolve(__dirname, 'assets/notifications/index.ts'),
        company_reports_js: path.resolve(__dirname, 'assets/company-reports/index.ts'),
        print_reports_js: path.resolve(__dirname, 'assets/company-reports/components/index.ts'),
        am_news_js: path.resolve(__dirname, 'assets/am-news/index.ts'),
        am_news_css: path.resolve(__dirname, 'assets/am-news/style.ts'),
        'general-settings_js': path.resolve(__dirname, 'assets/general-settings/index.ts'),
        market_place_js: path.resolve(__dirname, 'assets/market-place/index.ts'),
        media_releases_js: path.resolve(__dirname, 'assets/media-releases/index.ts'),
        monitoring_js: path.resolve(__dirname, 'assets/monitoring/index.ts'),
        factcheck_js: path.resolve(__dirname, 'assets/factcheck/index.ts'),
        common: path.resolve(__dirname, 'assets/common.ts'),
        design_js: path.resolve(__dirname, 'assets/design_pages.ts'),
        company_admin_js: path.resolve(__dirname, 'assets/company-admin/index.ts'),
        firebase_login_js: path.resolve(__dirname, 'assets/auth/firebase/login.ts'),
        firebase_reset_password_js: path.resolve(__dirname, 'assets/auth/firebase/reset_password.ts'),
        firebase_change_password_js: path.resolve(__dirname, 'assets/auth/firebase/change_password.ts'),
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
                test: /\.(ts|tsx|js|jsx)$/,
                include: [
                    path.resolve(__dirname, 'assets'),
                    path.resolve(__dirname, 'node_modules/bootstrap'),
                    path.resolve(process.cwd(), 'node_modules/bootstrap'),
                ],
                loader: 'ts-loader',
                options: {
                    transpileOnly: true,
                },
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
            {
                test: /\.(png|jpe?g|gif|svg|eot|ttf|woff|woff2)$/i,
                use: [
                    'file-loader',
                ],
            },
        ]
    },
    resolve: {
        extensions: [ '.ts', '.tsx', '.js', '.jsx'],
        modules: [
            path.resolve(__dirname, 'assets'),
            'node_modules',
        ],
        alias: {
            'moment-timezone': 'moment-timezone/builds/moment-timezone-with-data-10-year-range',
        },
        mainFields: ['browser', 'main'],
    },
    plugins: [
        new ObjectRestSpreadPlugin(),
        new ManifestPlugin({writeToFileEmit: true}),
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
    config.plugins.push(new webpack.DefinePlugin({
        'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV)
    }));
    config.plugins.push(new TerserPlugin({
        cache: true,
        parallel: true,
    }));
}

module.exports = config;
