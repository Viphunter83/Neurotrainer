// Learn more https://docs.expo.io/guides/customizing-metro
const { getDefaultConfig } = require('expo/metro-config');

/** @type {import('expo/metro-config').MetroConfig} */
const config = getDefaultConfig(__dirname);

// Optimize watchman to reduce EMFILE errors
config.watchFolders = [__dirname];

config.resolver = {
  ...config.resolver,
  // Reduce the number of files to watch by blocking unnecessary paths
  blockList: [
    // Exclude test files from bundling
    /.*\/__tests__\/.*/,
    /.*\/tests\/.*/,
    // Aggressively exclude node_modules to reduce file watching
    /node_modules\/.*\/node_modules\/.*/,
    /node_modules\/.*\/\.git\/.*/,
    /node_modules\/.*\/\.expo\/.*/,
    /node_modules\/.*\/android\/.*/,
    /node_modules\/.*\/ios\/.*/,
    /node_modules\/.*\/docs\/.*/,
    /node_modules\/.*\/examples\/.*/,
    /node_modules\/.*\/test\/.*/,
    /node_modules\/.*\/tests\/.*/,
    // Exclude build artifacts
    /.*\/\.expo\/.*/,
    /.*\/\.git\/.*/,
    /.*\/android\/build\/.*/,
    /.*\/ios\/build\/.*/,
    /.*\/\.idea\/.*/,
    /.*\/\.vscode\/.*/,
  ],
  // Optimize asset extensions
  assetExts: [
    ...config.resolver.assetExts,
    'db', 'mp3', 'ttf', 'obj', 'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg',
  ],
  // Optimize source extensions
  sourceExts: [...config.resolver.sourceExts, 'tsx', 'ts', 'jsx', 'js', 'json'],
};

// Reduce watcher overhead - optimize for large projects
config.watcher = {
  ...config.watcher,
  healthCheck: {
    enabled: true,
    interval: 30000, // Check every 30 seconds instead of default
  },
  // Use watchman if available, otherwise fallback to polling
  watchman: {
    deferStates: ['hg.update'],
  },
};

// Optimize transformer for better performance
config.transformer = {
  ...config.transformer,
  // Enable inline requires for better performance
  inlineRequires: true,
};

module.exports = config;

