module.exports = function(api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      // Required for Expo Router (if used in future)
      // 'expo-router/babel',
      // React Native Reanimated plugin (if used)
      // 'react-native-reanimated/plugin',
    ],
  };
};

