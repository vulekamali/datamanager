const { resolve } = require('path');
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const autoprefixer = require('autoprefixer');
const normalize = require('postcss-normalize');
const CleanWebpackPlugin = require('clean-webpack-plugin');


module.exports = {
  entry: {
    main: './_includes/scripts.js',
    webapp: 'webapp/src/index.js'
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
        query: { compact: false },
      },

      {
        test: /\.s?css$/,
        use: ExtractTextPlugin.extract(
          {
            fallback: 'style-loader',
            use: [
              {
                loader: 'css-loader',
                options: {
                  sourceMap: true,
                },
              },

              {
                loader: 'postcss-loader',
                options: {
                  sourceMap: true,
                  plugins: () => [
                    autoprefixer(),
                    normalize(),
                  ],
                },
              },

              {
                loader: 'sass-loader',
                options: {
                  sourceMap: true,
                },
              },
            ],
          },
        ),
      },
    ],
  },

  plugins: [
    new CleanWebpackPlugin('assets/generated/*'),
    new ExtractTextPlugin('styles.bundle.css')
  ],
};
