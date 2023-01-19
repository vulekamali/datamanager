const { resolve } = require('path');
// const ExtractTextPlugin = require('extract-text-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const autoprefixer = require('autoprefixer');
const normalize = require('postcss-normalize');
const CleanWebpackPlugin = require('clean-webpack-plugin');

module.exports = {
  entry: {
    'frontend-v1': './assets/js/scripts.js',
    'vulekamali-webflow': './assets/js/webflow/index.js',
  },
  output: {
    path: resolve(__dirname, 'assets/generated/'),
    filename: '[name].bundle.js',
  },

  devtool: 'source-map',

  module: {
    rules: [
      {
        test: /\.html$/,
        exclude: /node_modules/,
        use: { loader: 'html-loader' },
      },
      {
        test: /\.jsx?$/,
        loader: 'babel-loader',
        options: {
          presets: ['react']
        }
      },

      {
        test: /\.s?css$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          {
            loader: 'postcss-loader',
            options: {
              plugins: () => [
                autoprefixer(),
                normalize(),
              ],
            },
          },
          'sass-loader',
        ],
      },
    ],
  },

  plugins: [
     new MiniCssExtractPlugin({filename: 'styles.bundle.css'}),
  ]
};
