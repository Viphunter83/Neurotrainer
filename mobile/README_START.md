# Инструкция по запуску приложения

## Проблема EMFILE (too many open files)

Если вы сталкиваетесь с ошибкой `EMFILE: too many open files`, используйте один из следующих методов:

### Метод 1: Использовать скрипт запуска (рекомендуется)
```bash
./start-expo.sh
```

### Метод 2: Установить watchman (лучшее решение)
```bash
brew install watchman
```
После установки watchman, Metro будет использовать его вместо Node.js file watcher, что решит проблему EMFILE.

### Метод 3: Ручной запуск с переменными окружения
```bash
export CHOKIDAR_USEPOLLING=true
export CHOKIDAR_INTERVAL=1000
ulimit -n 20480
npx expo start --clear
```

### Метод 4: Увеличить системный лимит (macOS)
Добавьте в `~/.zshrc` или `~/.bash_profile`:
```bash
ulimit -n 20480
```

## Обычный запуск (если нет проблем с EMFILE)
```bash
npx expo start --clear
```

## Запуск для конкретной платформы
```bash
npx expo start --ios      # iOS симулятор
npx expo start --android  # Android эмулятор
npx expo start --web      # Web браузер
```

