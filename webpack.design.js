/* eslint-env node */

const path = require('path');
const HtmlWebPackPlugin = require('html-webpack-plugin');
const { WebpackManifestPlugin } = require('webpack-manifest-plugin');

const config = {
    entry: {
        main: path.resolve(__dirname, 'design_app/src/index.js'),
    },
    output: {
        path: path.resolve(process.cwd(), 'dist'),
        publicPath: '/',
        filename: '[name].[hash].js',
        chunkFilename: '[id].[hash].js',
    },
    devServer: {
        port: 3042,
        historyApiFallback: true,
        open: true,
        static: {
            directory: path.join(__dirname, 'newsroom', 'static'),
            publicPath: '/static/',
        },
    },
    module: {
        rules: [
            {
                test: /\.(ts|tsx|js|jsx)$/,
                include: [
                    path.resolve(__dirname, 'design_app/src'),
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
        ],
    },
    resolve: {
        extensions: [ '.ts', '.tsx', '.js', '.jsx'],
        modules: [
            path.resolve(__dirname, 'design_app/src'),
            path.resolve(__dirname, 'assets'),
            'node_modules',
        ],
        alias: {
            'moment-timezone': 'moment-timezone/builds/moment-timezone-with-data-10-year-range',
        },
        mainFields: ['browser', 'main'],
    },
    plugins: [
        new HtmlWebPackPlugin({
            template: path.resolve(__dirname, 'design_app/public', 'index.html'),
        }),
        new WebpackManifestPlugin(),
    ],
};

module.exports = config;
