# Настройка базы данных

## Вариант 1: PostgreSQL (рекомендуется)

### Установка через Homebrew

```bash
# Установить PostgreSQL
brew install postgresql@14

# Запустить PostgreSQL
brew services start postgresql@14

# Создать базу данных
createdb fitness_ai

# Создать пользователя (опционально)
psql postgres
CREATE USER fitness_user WITH PASSWORD 'fitness_pass';
GRANT ALL PRIVILEGES ON DATABASE fitness_ai TO fitness_user;
\q
```

### Настройка .env

Убедитесь, что в `.env` файле указан правильный DATABASE_URL:

```bash
DATABASE_URL=postgresql://fitness_user:fitness_pass@localhost:5432/fitness_ai
```

### Применение миграций

```bash
# Активировать виртуальное окружение
source venv/bin/activate

# Применить миграции
alembic upgrade head
```

## Вариант 2: Docker (альтернатива)

Если не хотите устанавливать PostgreSQL напрямую:

```bash
# Запустить PostgreSQL в Docker
docker run --name fitnessai-postgres \
  -e POSTGRES_USER=fitness_user \
  -e POSTGRES_PASSWORD=fitness_pass \
  -e POSTGRES_DB=fitness_ai \
  -p 5432:5432 \
  -d postgres:14

# Применить миграции
alembic upgrade head
```

## Вариант 3: SQLite (для быстрого тестирования)

Если нужно быстро протестировать без PostgreSQL, можно временно использовать SQLite:

1. Изменить `src/config.py`:
```python
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "sqlite:///./fitnessai.db",  # SQLite вместо PostgreSQL
)
```

2. Обновить `src/database/database.py`:
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # Для SQLite
    poolclass=StaticPool,
)
```

**Внимание:** SQLite не поддерживает все функции PostgreSQL (например, ARRAY, UUID). Для production используйте PostgreSQL.

## Проверка подключения

```bash
# Проверить подключение к PostgreSQL
psql -U fitness_user -d fitness_ai -h localhost

# Или через Python
python3 -c "
from src.database.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT version()'))
    print(result.fetchone())
"
```

