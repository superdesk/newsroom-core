const config = require('../webpack.config');

config.devServer = {
    compress: true,
    disableHostCheck: true,
};

module.exports = config;
