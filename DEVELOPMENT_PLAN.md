# План разработки и запуска FitnessAI

## Текущее состояние

### ✅ Что уже сделано:
- ✅ Исправлены критические баги (валидация пароля, PushToken модель)
- ✅ Создан `.gitignore` для правильного управления файлами
- ✅ Миграция базы данных для PushToken готова
- ✅ Базовая структура проекта (модели, экраны авторизации)

### ⚠️ Что нужно восстановить:
- ❌ Backend сервер (main.py, config.py, database.py, API endpoints)
- ❌ Mobile app структура (App.tsx, навигация, store, компоненты)
- ❌ Конфигурационные файлы (requirements.txt, package.json, alembic.ini)
- ❌ База данных (настройка PostgreSQL, применение миграций)

---

## Этап 1: Восстановление базовой структуры проекта

### 1.1 Backend (Python/FastAPI)
**Приоритет: КРИТИЧЕСКИЙ**

Необходимо восстановить:
- `requirements.txt` - зависимости Python
- `src/main.py` - точка входа FastAPI приложения
- `src/config.py` - конфигурация (база данных, JWT, CORS)
- `src/database/database.py` - подключение к БД
- `src/api/v1/endpoints/` - API endpoints (auth, users, exercises)
- `src/services/` - бизнес-логика
- `alembic.ini` - конфигурация миграций

**Оценка времени:** 2-3 часа

### 1.2 Mobile App (React Native/Expo)
**Приоритет: КРИТИЧЕСКИЙ**

Необходимо восстановить:
- `mobile/package.json` - зависимости Node.js
- `mobile/App.tsx` - точка входа приложения
- `mobile/src/store/` - Redux store и slices
- `mobile/src/navigation/` - навигация (React Navigation)
- `mobile/src/components/` - переиспользуемые компоненты
- `mobile/app.json` - конфигурация Expo

**Оценка времени:** 2-3 часа

---

## Этап 2: Настройка окружения

### 2.1 База данных
**Приоритет: КРИТИЧЕСКИЙ**

1. Установить PostgreSQL (если не установлен)
2. Создать базу данных:
   ```bash
   createdb fitnessai
   ```
3. Настроить `.env` файл:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/fitnessai
   ```
4. Применить миграции:
   ```bash
   alembic upgrade head
   ```

**Оценка времени:** 30 минут

### 2.2 Backend зависимости
```bash
cd /Users/apple/Neurotrainer
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2.3 Mobile зависимости
```bash
cd /Users/apple/Neurotrainer/mobile
npm install
```

**Оценка времени:** 15 минут

---

## Этап 3: Настройка Firebase для Push Notifications

**Приоритет: ВАЖНЫЙ**

### 3.1 Создание Firebase проекта
1. Перейти на [Firebase Console](https://console.firebase.google.com/)
2. Создать новый проект "FitnessAI"
3. Добавить iOS приложение (Bundle ID из app.json)
4. Добавить Android приложение (Package name из app.json)
5. Скачать конфигурационные файлы:
   - `google-services.json` (Android) → `mobile/android/app/`
   - `GoogleService-Info.plist` (iOS) → `mobile/ios/`

### 3.2 Настройка Backend
1. Получить Service Account Key из Firebase Console
2. Добавить в `.env`:
   ```
   FIREBASE_CREDENTIALS_PATH=/path/to/service-account-key.json
   ```
3. Раскомментировать код в `src/services/push_notification_service.py`

### 3.3 Настройка Mobile App
1. Установить Firebase SDK:
   ```bash
   cd mobile
   npm install @react-native-firebase/app @react-native-firebase/messaging
   ```
2. Раскомментировать код в `mobile/src/services/push-notification.service.ts`
3. Настроить нативные модули (требуется native build)

**Оценка времени:** 1-2 часа

---

## Этап 4: Настройка Vision Camera

**Приоритет: ВАЖНЫЙ**

### 4.1 Создание Native Build
Vision Camera требует нативного билда (не работает в Expo Go):

```bash
cd mobile
npx expo prebuild
npx expo run:ios  # или npx expo run:android
```

### 4.2 Переключение на CameraScreen
После успешного билда:
1. Обновить навигацию для использования `CameraScreen.tsx` вместо `ExpoCameraScreen`
2. Протестировать работу камеры

**Оценка времени:** 1 час (после native build)

---

## Этап 5: Запуск и тестирование

### 5.1 Запуск Backend
```bash
cd /Users/apple/Neurotrainer
source venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**Проверка:**
- `http://localhost:8000/docs` - Swagger UI
- `http://localhost:8000/health` - Health check

### 5.2 Запуск Mobile App
```bash
cd mobile
npx expo start
```

**Варианты:**
- Expo Go (для быстрого тестирования, без Vision Camera)
- Native build (для полного функционала)

**Оценка времени:** 30 минут

---

## Этап 6: Приоритетные улучшения (Priority 3)

После того, как основное приложение работает:

1. **Тестирование**
   - Unit тесты для backend
   - Unit тесты для mobile app
   - Integration тесты

2. **Безопасность**
   - Проверка всех endpoints на авторизацию
   - Валидация входных данных
   - Rate limiting

3. **Производительность**
   - Оптимизация запросов к БД
   - Кэширование
   - Оптимизация ML inference

4. **Документация**
   - API документация
   - README с инструкциями
   - Комментарии в коде

---

## Рекомендуемый порядок выполнения

### Сейчас (критично):
1. ✅ Восстановить `requirements.txt` и backend структуру
2. ✅ Восстановить `package.json` и mobile структуру
3. ✅ Настроить базу данных и применить миграции
4. ✅ Запустить backend сервер
5. ✅ Запустить mobile app в Expo Go

### Далее (важно):
6. Настроить Firebase для Push Notifications
7. Создать native build для Vision Camera
8. Переключиться на Vision Camera

### Потом (улучшения):
9. Добавить тесты
10. Улучшить безопасность
11. Оптимизировать производительность

---

## Команды для быстрого старта

```bash
# 1. Backend
cd /Users/apple/Neurotrainer
python3.10 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy alembic psycopg2-binary python-dotenv
alembic upgrade head
python -m uvicorn src.main:app --reload

# 2. Mobile (в другом терминале)
cd /Users/apple/Neurotrainer/mobile
npm install
npx expo start
```

---

## Проблемы и решения

### Проблема: Файлы удалены из Git истории
**Решение:** Восстановить структуру на основе существующих директорий и моделей

### Проблема: База данных не настроена
**Решение:** Использовать локальный PostgreSQL или Docker контейнер

### Проблема: Firebase требует настройки
**Решение:** Можно отложить до этапа 3, приложение будет работать без push notifications

### Проблема: Vision Camera требует native build
**Решение:** Использовать Expo Camera для разработки, переключиться на Vision Camera позже

