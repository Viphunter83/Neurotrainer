#!/bin/bash
# Start Expo with optimized file watching
export CHOKIDAR_USEPOLLING=true
export CHOKIDAR_INTERVAL=1000
ulimit -n 20480
npx expo start --clear
