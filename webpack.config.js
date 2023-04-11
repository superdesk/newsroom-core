/* eslint-env node */

import {resolve as _resolve} from 'path';
import {optimize, DefinePlugin} from 'webpack';
import ManifestPlugin from 'webpack-manifest-plugin';
import TerserPlugin from 'terser-webpack-plugin-legacy';

const config = {
    entry: {
        newsroom_ts: _resolve(__dirname, 'assets/index.ts'),
        companies_ts: _resolve(__dirname, 'assets/companies/index.ts'),
        oauth_clients_ts: _resolve(__dirname, 'assets/oauth_clients/index.ts'),
        users_ts: _resolve(__dirname, 'assets/users/index.ts'),
        products_ts: _resolve(__dirname, 'assets/products/index.ts'),
        'section-filters_ts': _resolve(__dirname, 'assets/section-filters/index.ts'),
        navigations_ts: _resolve(__dirname, 'assets/navigations/index.ts'),
        cards_ts: _resolve(__dirname, 'assets/cards/index.ts'),
        user_profile_ts: _resolve(__dirname, 'assets/user-profile/index.ts'),
        newsroom_css: _resolve(__dirname, 'assets/style.ts'),
        wire_ts: _resolve(__dirname, 'assets/wire/index.ts'),
        home_ts: _resolve(__dirname, 'assets/home/index.ts'),
        agenda_ts: _resolve(__dirname, 'assets/agenda/index.ts'),
        notifications_ts: _resolve(__dirname, 'assets/notifications/index.ts'),
        company_reports_ts: _resolve(__dirname, 'assets/company-reports/index.ts'),
        print_reports_ts: _resolve(__dirname, 'assets/company-reports/components/index.ts'),
        am_news_ts: _resolve(__dirname, 'assets/am-news/index.ts'),
        am_news_css: _resolve(__dirname, 'assets/am-news/style.ts'),
        'general-settings_ts': _resolve(__dirname, 'assets/general-settings/index.ts'),
        market_place_ts: _resolve(__dirname, 'assets/market-place/index.ts'),
        media_releases_ts: _resolve(__dirname, 'assets/media-releases/index.ts'),
        monitoring_ts: _resolve(__dirname, 'assets/monitoring/index.ts'),
        factcheck_ts: _resolve(__dirname, 'assets/factcheck/index.ts'),
        common: _resolve(__dirname, 'assets/common.ts'),
        design_ts: _resolve(__dirname, 'assets/design_pages.ts'),
        company_admin_ts: _resolve(__dirname, 'assets/company-admin/index.ts'),
    },
    output: {
        path: _resolve(process.cwd(), 'dist'),
        publicPath: 'http://localhost:8080/',
        filename: '[name].[chunkhash].js',
        chunkFilename: '[id].[chunkhash].js'
    },
    devtool: 'source-map',
    module: {
        rules: [
            {
                test: /\.tsx?$/,
                loader: 'ts-loader'
            },
            {
                test: /\.tsx?$/,
                include: [
                    _resolve(__dirname, 'assets'),
                    _resolve(__dirname, 'node_modules/bootstrap'),
                    _resolve(process.cwd(), 'node_modules/bootstrap'),
                ],
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
            {
                test: /\.(png|jpe?g|gif|svg|eot|ttf|woff|woff2)$/i,
                use: [
                    'file-loader',
                ],
            },
        ]
    },
    resolve: {
        extensions: ['.ts', '.tsx'],
        modules: [
            _resolve(__dirname, 'assets'),
            'node_modules',
        ],
        alias: {
            'moment-timezone': 'moment-timezone/builds/moment-timezone-with-data-10-year-range',
        },
        mainFields: ['browser', 'main'],
    },
    plugins: [
        new ManifestPlugin(),
        new optimize.CommonsChunkPlugin({
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
    config.plugins.push(new DefinePlugin({
        'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV)
    }));
    config.plugins.push(new TerserPlugin({
        cache: true,
        parallel: true,
    }));
}

export default config;
