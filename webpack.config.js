const webpack = require('webpack');

module.exports = {
    entry: './src/limiter.js',
    mode: 'production',
    plugins: [
        new webpack.BannerPlugin({
            banner: '#!js name=limiter api_version=1.0',
            raw: true,
            entryOnly: true
        })
    ]
};