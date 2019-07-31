module.exports = ({ config }) => {
  config.module.rules.push({
    test: /\.(tsx?)$/,
    loader: require.resolve('babel-loader'),
    options: {
      presets: [['react-app', { flow: false, typescript: true, corejs: 2 }]],
    },
  });
  config.resolve.extensions.push('.ts', '.tsx');
  return config;
};