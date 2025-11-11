# Руководство по тестированию FitnessAI

## Быстрый старт

### 1. Запуск Backend сервера

```bash
cd /Users/apple/Neurotrainer
source venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**Проверка:**
- Откройте http://localhost:8000/docs - Swagger UI
- Откройте http://localhost:8000/health - Health check

### 2. Установка зависимостей Mobile App

```bash
cd /Users/apple/Neurotrainer/mobile
npm install
```

### 3. Запуск Mobile App

```bash
cd /Users/apple/Neurotrainer/mobile
npx expo start
```

**Варианты запуска:**
- `i` - iOS симулятор
- `a` - Android эмулятор
- Сканировать QR код в Expo Go (для физического устройства)

---

## Тестирование API Endpoints

### 1. Health Check

```bash
curl http://localhost:8000/health
```

**Ожидаемый результат:**
```json
{
  "status": "healthy",
  "service": "FitnessAI Backend",
  "version": "0.1.0"
}
```

### 2. Регистрация пользователя

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "Test123!@#",
    "full_name": "Test User"
  }'
```

**Ожидаемый результат:**
```json
{
  "id": "...",
  "email": "test@example.com",
  "username": "testuser",
  "full_name": "Test User",
  "is_active": true,
  "created_at": "..."
}
```

### 3. Вход пользователя

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#"
  }'
```

**Ожидаемый результат:**
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

**Сохраните токены для следующих запросов:**
```bash
export ACCESS_TOKEN="ваш_access_token"
export REFRESH_TOKEN="ваш_refresh_token"
```

### 4. Регистрация Push Token

```bash
curl -X POST http://localhost:8000/api/v1/push-tokens/register \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "token": "ExponentPushToken[test-token-123]",
    "platform": "ios",
    "device_id": "iPhone-13-Pro"
  }'
```

**Ожидаемый результат:**
```json
{
  "id": "...",
  "token": "ExponentPushToken[test-token-123]",
  "platform": "ios",
  "is_active": true
}
```

### 5. Обновление токена (Refresh)

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "$REFRESH_TOKEN"
  }'
```

### 6. Выход (Logout)

```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Content-Type: application/json" \
  -d '{
    "access_token": "$ACCESS_TOKEN",
    "refresh_token": "$REFRESH_TOKEN"
  }'
```

---

## Тестирование Mobile App

### 1. Запуск в Expo Go

1. Установите Expo Go на телефон (iOS/Android)
2. Запустите `npx expo start`
3. Отсканируйте QR код в Expo Go

### 2. Тестирование экранов

**Login Screen:**
- Введите email и password
- Проверьте валидацию (неправильный email, слабый пароль)
- Попробуйте войти с неверными данными
- Попробуйте войти с правильными данными

**Register Screen:**
- Заполните форму регистрации
- Проверьте валидацию всех полей
- Зарегистрируйте нового пользователя

### 3. Тестирование Push Notifications

1. После входа в приложение, токен должен автоматически зарегистрироваться
2. Проверьте в логах, что токен отправлен на backend
3. Отправьте тестовое уведомление через API (см. ниже)

---

## Отправка тестового Push Notification

### Через Python скрипт

Создайте файл `test_push.py`:

```python
import asyncio
from src.services.push_notification_service import send_push_notification
from src.database.database import get_db
from uuid import UUID

async def test_push():
    # Замените на реальный user_id из базы данных
    user_id = UUID("ваш-user-id")
    
    db = next(get_db())
    try:
        success = await send_push_notification(
            user_id=user_id,
            title="Test Notification",
            body="Это тестовое уведомление!",
            data={"type": "test"},
            db=db,
        )
        print(f"✅ Уведомление отправлено: {success}")
    finally:
        try:
            next(get_db())
        except StopIteration:
            pass

if __name__ == "__main__":
    asyncio.run(test_push())
```

Запуск:
```bash
cd /Users/apple/Neurotrainer
source venv/bin/activate
python test_push.py
```

---

## Проверка базы данных

### Подключение к PostgreSQL

```bash
export PATH="/opt/homebrew/opt/postgresql@14/bin:$PATH"
psql -U fitness_user -d fitness_ai -h localhost
```

### Полезные SQL запросы

```sql
-- Проверить пользователей
SELECT id, email, username, is_active, created_at FROM users;

-- Проверить push tokens
SELECT id, user_id, platform, is_active, created_at FROM push_tokens;

-- Проверить токены пользователя
SELECT pt.* FROM push_tokens pt
JOIN users u ON pt.user_id = u.id
WHERE u.email = 'test@example.com';
```

---

## Автоматизированное тестирование

### Backend тесты (будущее)

```bash
cd /Users/apple/Neurotrainer
source venv/bin/activate
pytest tests/
```

### Mobile app тесты (будущее)

```bash
cd /Users/apple/Neurotrainer/mobile
npm test
```

---

## Troubleshooting

### Backend не запускается

1. Проверьте, что PostgreSQL запущен:
   ```bash
   brew services list | grep postgresql
   ```

2. Проверьте DATABASE_URL в .env

3. Проверьте, что все зависимости установлены:
   ```bash
   pip install -r requirements.txt
   ```

### Mobile app не запускается

1. Убедитесь, что зависимости установлены:
   ```bash
   cd mobile && npm install
   ```

2. Очистите кэш:
   ```bash
   npx expo start --clear
   ```

3. Проверьте, что backend доступен:
   ```bash
   curl http://localhost:8000/health
   ```

### Push Notifications не работают

1. Проверьте, что Firebase Service Account Key настроен:
   ```bash
   cat .env | grep FIREBASE_CREDENTIALS_PATH
   ```

2. Проверьте, что токен зарегистрирован в базе данных

3. Проверьте логи backend для ошибок

---

## Чеклист тестирования

- [ ] Backend сервер запускается
- [ ] Health check работает
- [ ] Регистрация пользователя работает
- [ ] Вход пользователя работает
- [ ] JWT токены генерируются правильно
- [ ] Refresh token работает
- [ ] Logout работает
- [ ] Push token регистрация работает
- [ ] Mobile app запускается
- [ ] Login screen работает
- [ ] Register screen работает
- [ ] Валидация форм работает
- [ ] API интеграция работает
- [ ] Push notifications регистрируются
- [ ] Тестовое уведомление отправляется

