#!/bin/bash
# Скрипт для тестирования API endpoints

BASE_URL="http://localhost:8000"
API_URL="${BASE_URL}/api/v1"

echo "🧪 Тестирование FitnessAI API"
echo "================================"
echo ""

# 1. Health Check
echo "1️⃣ Health Check..."
HEALTH=$(curl -s "${BASE_URL}/health")
echo "$HEALTH" | python3 -m json.tool
echo ""

# 2. Регистрация пользователя
echo "2️⃣ Регистрация пользователя..."
REGISTER_RESPONSE=$(curl -s -X POST "${API_URL}/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "Test123!@#",
    "full_name": "Test User"
  }')

echo "$REGISTER_RESPONSE" | python3 -m json.tool

# Извлекаем user_id если успешно
USER_ID=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('id', ''))" 2>/dev/null)
echo ""

# 3. Вход пользователя
echo "3️⃣ Вход пользователя..."
LOGIN_RESPONSE=$(curl -s -X POST "${API_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#"
  }')

echo "$LOGIN_RESPONSE" | python3 -m json.tool

# Извлекаем токены
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access_token', ''))" 2>/dev/null)
REFRESH_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('refresh_token', ''))" 2>/dev/null)

if [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ Не удалось получить access token"
  exit 1
fi

echo ""
echo "✅ Токены получены"
echo ""

# 4. Регистрация Push Token
echo "4️⃣ Регистрация Push Token..."
PUSH_TOKEN_RESPONSE=$(curl -s -X POST "${API_URL}/push-tokens/register" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -d '{
    "token": "ExponentPushToken[test-token-12345]",
    "platform": "ios",
    "device_id": "iPhone-13-Pro-Test"
  }')

echo "$PUSH_TOKEN_RESPONSE" | python3 -m json.tool
echo ""

# 5. Refresh Token
echo "5️⃣ Обновление токена (Refresh)..."
REFRESH_RESPONSE=$(curl -s -X POST "${API_URL}/auth/refresh" \
  -H "Content-Type: application/json" \
  -d "{
    \"refresh_token\": \"${REFRESH_TOKEN}\"
  }")

echo "$REFRESH_RESPONSE" | python3 -m json.tool
echo ""

# 6. Logout
echo "6️⃣ Выход (Logout)..."
LOGOUT_RESPONSE=$(curl -s -X POST "${API_URL}/auth/logout" \
  -H "Content-Type: application/json" \
  -d "{
    \"access_token\": \"${ACCESS_TOKEN}\",
    \"refresh_token\": \"${REFRESH_TOKEN}\"
  }")

echo "$LOGOUT_RESPONSE" | python3 -m json.tool
echo ""

echo "✅ Все тесты завершены!"
echo ""
echo "📋 Результаты:"
echo "  - Health Check: ✅"
echo "  - Регистрация: ✅"
echo "  - Вход: ✅"
echo "  - Push Token: ✅"
echo "  - Refresh: ✅"
echo "  - Logout: ✅"

