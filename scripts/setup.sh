#!/usr/bin/env bash
set -euo pipefail

# ──────────────────────────────────────────────────────────────────────────────
#  refero — setup script
#  Создаёт .env, поднимает контейнеры, накатывает миграции, сидирует БД.
#  Запускать из корня проекта: ./scripts/setup.sh
# ──────────────────────────────────────────────────────────────────────────────

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# ── Читаем порты из .env (если есть) ──────────────────────────────────────────
source_env() {
  local f="$1"
  [ -f "$f" ] && while IFS='=' read -r k v; do
    [ -n "$k" ] && [[ "$k" != "#"* ]] && export "$k"="$v"
  done < "$f" || true
}
source_env .env
source_env backend/.env

BACKEND_PORT="${BACKEND_PORT:-8000}"
CLIENT_PORT="${CLIENT_PORT:-8080}"

# ── 1. Проверка зависимостей ──────────────────────────────────────────────────
echo "🔍 Проверяю Docker..."

if ! command -v docker &>/dev/null; then
  echo "❌ Docker не найден."
  echo "   Установите Docker: https://docs.docker.com/get-docker/"
  exit 1
fi

if ! docker compose version &>/dev/null; then
  echo "❌ Docker Compose plugin не найден."
  echo "   Установите: https://docs.docker.com/compose/install/"
  exit 1
fi

# ── 2. .env файлы ─────────────────────────────────────────────────────────────
echo "📄 Настраиваю .env файлы..."

if [ ! -f .env ]; then
  cp .env-example .env
  echo "   Создан .env (из .env-example)"
else
  echo "   .env уже существует — пропускаю"
fi

if [ ! -f backend/.env ]; then
  cp backend/.env-example backend/.env
  echo "   Создан backend/.env (из backend/.env-example)"
else
  echo "   backend/.env уже существует — пропускаю"
fi

mkdir -p backend/uploads

# ── 3. Сборка и запуск ────────────────────────────────────────────────────────
echo "🐳 Собираю и запускаю контейнеры..."
docker compose up -d --build

# ── 4. Ожидание PostgreSQL ────────────────────────────────────────────────────
echo "⏳ Жду PostgreSQL..."
for i in $(seq 1 30); do
  if docker compose exec -T db pg_isready -U refero -d refero_db &>/dev/null; then
    echo "   PostgreSQL готов!"
    break
  fi
  if [ "$i" -eq 30 ]; then
    echo "❌ PostgreSQL не поднялся за 30 секунд."
    echo "   Проверьте логи: docker compose logs db"
    exit 1
  fi
  sleep 2
done

# ── 5. Ожидание backend (alembic migration + uvicorn) ─────────────────────────
echo "⏳ Жду backend..."
for i in $(seq 1 30); do
  # Проверяем, что процесс uvicorn запущен в контейнере
  if docker compose exec -T backend sh -c "pgrep -f uvicorn" &>/dev/null; then
    echo "   Backend готов (uvicorn запущен)!"
    sleep 2
    break
  fi
  if [ "$i" -eq 30 ]; then
    echo "❌ Backend не поднялся за 30 секунд."
    echo "   Проверьте логи: docker compose logs backend"
    exit 1
  fi
  sleep 2
done

# ── 6. Seed ────────────────────────────────────────────────────────────────────
echo "🌱 Сидирую БД..."
docker compose exec -T backend python seed.py

# ── 7. Готово ─────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ refero запущен!"
echo ""
echo "  Frontend  → http://localhost:${CLIENT_PORT}"
echo "  Backend   → http://localhost:${BACKEND_PORT}"
echo "  Docs      → http://localhost:${BACKEND_PORT}/docs"
echo ""
echo "  Учётные данные для входа:"
echo "    admin      / admin123     (ADMIN)"
echo "    ivanov     / author123    (AUTHOR)"
echo "    petrova    / author123    (AUTHOR)"
echo "    sidorov    / author123    (AUTHOR + REVIEWER)"
echo "    kuznetsova / reviewer123  (REVIEWER)"
echo "    smirnov    / author123    (AUTHOR)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Команды:"
echo "    Остановить:    docker compose down"
echo "    Логи:          docker compose logs -f"
echo "    Сид заново:    docker compose exec -T backend python seed.py"
echo "    Bash в backend: docker compose exec backend bash"
echo "    Sh в frontend:  docker compose exec frontend sh"
echo ""
