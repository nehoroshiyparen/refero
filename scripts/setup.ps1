<#
.SYNOPSIS
  refero — скрипт первоначальной настройки проекта (Windows/PowerShell).

.DESCRIPTION
  - Создаёт .env файлы (из примеров), если их нет
  - Собирает и запускает Docker-контейнеры
  - Накатывает миграции (alembic)
  - Сидирует БД тестовыми данными
  - Выводит учётные данные

  Запускать из корня проекта:
    PowerShell -ExecutionPolicy Bypass -File scripts\setup.ps1
#>

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $PSScriptRoot
Set-Location $ROOT

# ── Функция чтения .env ───────────────────────────────────────────────────────
function Get-EnvVar($file, $key) {
  if (-not (Test-Path $file)) { return $null }
  Get-Content $file | ForEach-Object {
    if ($_ -match "^$key\s*=\s*(.+)$") { return $matches[1].Trim() }
  }
  return $null
}

$BACKEND_PORT = Get-EnvVar ".env" "BACKEND_PORT"
if (-not $BACKEND_PORT) { $BACKEND_PORT = "8000" }

$CLIENT_PORT = Get-EnvVar ".env" "CLIENT_PORT"
if (-not $CLIENT_PORT) { $CLIENT_PORT = "8080" }

# ── 1. Проверка Docker ────────────────────────────────────────────────────────
Write-Host "🔍 Проверяю Docker..." -ForegroundColor Cyan

$docker = Get-Command docker -ErrorAction SilentlyContinue
if (-not $docker) {
  Write-Host "❌ Docker не найден." -ForegroundColor Red
  Write-Host ""
  Write-Host "    Скачайте и установите Docker Desktop:" -ForegroundColor Yellow
  Write-Host "    https://docs.docker.com/desktop/setup/install/windows-install/" -ForegroundColor Yellow
  Write-Host ""
  Write-Host "    После установки перезапустите терминал и запустите скрипт снова." -ForegroundColor Yellow
  exit 1
}

$compose = docker compose version 2>&1
if ($LASTEXITCODE -ne 0) {
  Write-Host "❌ Docker Compose не работает. Убедитесь, что Docker Desktop запущен." -ForegroundColor Red
  exit 1
}

# ── 2. .env файлы ─────────────────────────────────────────────────────────────
Write-Host "📄 Настраиваю .env файлы..." -ForegroundColor Cyan

if (-not (Test-Path .env)) {
  Copy-Item .env-example .env
  Write-Host "   Создан .env (из .env-example)" -ForegroundColor Green
} else {
  Write-Host "   .env уже существует — пропускаю" -ForegroundColor Gray
}

if (-not (Test-Path backend\.env)) {
  Copy-Item backend\.env-example backend\.env
  Write-Host "   Создан backend/.env (из backend/.env-example)" -ForegroundColor Green
} else {
  Write-Host "   backend/.env уже существует — пропускаю" -ForegroundColor Gray
}

if (-not (Test-Path backend\uploads)) {
  New-Item -ItemType Directory -Path backend\uploads -Force | Out-Null
}

# ── 3. Сборка и запуск ────────────────────────────────────────────────────────
Write-Host "🐳 Собираю и запускаю контейнеры..." -ForegroundColor Cyan
docker compose up -d --build
if ($LASTEXITCODE -ne 0) {
  Write-Host "❌ Ошибка при сборке/запуске контейнеров." -ForegroundColor Red
  exit 1
}

# ── 4. Ожидание PostgreSQL ────────────────────────────────────────────────────
Write-Host "⏳ Жду PostgreSQL..." -ForegroundColor Cyan
$ready = $false
for ($i = 1; $i -le 30; $i++) {
  $result = docker compose exec -T db pg_isready -U refero -d refero_db 2>&1
  if ($LASTEXITCODE -eq 0) {
    Write-Host "   PostgreSQL готов!" -ForegroundColor Green
    $ready = $true
    break
  }
  Start-Sleep -Seconds 2
}
if (-not $ready) {
  Write-Host "❌ PostgreSQL не поднялся за 30 секунд." -ForegroundColor Red
  Write-Host "   Проверьте логи: docker compose logs db" -ForegroundColor Yellow
  exit 1
}

# ── 5. Ожидание backend ───────────────────────────────────────────────────────
Write-Host "⏳ Жду backend..." -ForegroundColor Cyan
$ready = $false
for ($i = 1; $i -le 30; $i++) {
  $result = docker compose exec -T backend sh -c "pgrep -f uvicorn" 2>&1
  if ($LASTEXITCODE -eq 0) {
    Write-Host "   Backend готов!" -ForegroundColor Green
    $ready = $true
    Start-Sleep -Seconds 2
    break
  }
  Start-Sleep -Seconds 2
}
if (-not $ready) {
  Write-Host "❌ Backend не поднялся за 30 секунд." -ForegroundColor Red
  Write-Host "   Проверьте логи: docker compose logs backend" -ForegroundColor Yellow
  exit 1
}

# ── 6. Seed ────────────────────────────────────────────────────────────────────
Write-Host "🌱 Сидирую БД..." -ForegroundColor Cyan
docker compose exec -T backend python seed.py
if ($LASTEXITCODE -ne 0) {
  Write-Host "❌ Ошибка при сидировании." -ForegroundColor Red
  exit 1
}

# ── 7. Готово ─────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  ✅ refero запущен!" -ForegroundColor Green
Write-Host ""
Write-Host "  Frontend  → http://localhost:$CLIENT_PORT" -ForegroundColor White
Write-Host "  Backend   → http://localhost:$BACKEND_PORT" -ForegroundColor White
Write-Host "  Docs      → http://localhost:$BACKEND_PORT/docs" -ForegroundColor White
Write-Host ""
Write-Host "  Учётные данные для входа:" -ForegroundColor Yellow
Write-Host "    admin      / admin123     (ADMIN)"
Write-Host "    ivanov     / author123    (AUTHOR)"
Write-Host "    petrova    / author123    (AUTHOR)"
Write-Host "    sidorov    / author123    (AUTHOR + REVIEWER)"
Write-Host "    kuznetsova / reviewer123  (REVIEWER)"
Write-Host "    smirnov    / author123    (AUTHOR)"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Команды:" -ForegroundColor Gray
Write-Host "    Остановить:    docker compose down"
Write-Host "    Логи:          docker compose logs -f"
Write-Host "    Сид заново:    docker compose exec -T backend python seed.py"
Write-Host "    Bash в backend: docker compose exec backend bash"
Write-Host "    Sh в frontend:  docker compose exec frontend sh"
Write-Host ""
