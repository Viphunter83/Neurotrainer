# Быстрый старт FitnessAI

## 🚀 Запуск Backend

```bash
cd /Users/apple/Neurotrainer
source venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**Проверка:**
- http://localhost:8000/docs - Swagger UI
- http://localhost:8000/health - Health check

## 📱 Запуск Mobile App

```bash
cd /Users/apple/Neurotrainer/mobile
npm install  # Первый раз
npx expo start
```

**Варианты:**
- Нажмите `i` для iOS симулятора
- Нажмите `a` для Android эмулятора
- Отсканируйте QR код в Expo Go (физическое устройство)

## 🧪 Тестирование API

Запустите автоматический тест:
```bash
cd /Users/apple/Neurotrainer
./test_api.sh
```

Или тестируйте вручную через Swagger UI:
- Откройте http://localhost:8000/docs
- Попробуйте endpoints:
  - `POST /api/v1/auth/register` - Регистрация
  - `POST /api/v1/auth/login` - Вход
  - `POST /api/v1/push-tokens/register` - Регистрация push token

## 📋 Чеклист готовности

- [x] Backend сервер работает
- [x] База данных настроена
- [x] API endpoints работают
- [x] Firebase настроен
- [x] Push Notifications готовы
- [ ] Mobile app зависимости установлены
- [ ] Mobile app запущен и протестирован

## 🔗 Полезные ссылки

- **API документация:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health
- **Подробное руководство:** TESTING_GUIDE.md

