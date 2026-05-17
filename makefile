.PHONY: start stop logs build rebuild restart ps clean \
        bash-back bash-front \

# 🚀 Запуск
start:
	docker compose up -d

# 🛑 Остановка
stop:
	docker compose down

# 🔨 Сборка
build:
	docker compose build

# 💣 Полная пересборка
rebuild:
	docker compose down -v
	docker compose up -d --build

# 🔄 Рестарт
restart:
	docker compose down
	docker compose up -d

clean:
	docker compose down -v

# 📜 Логи
logs:
	docker compose logs -f

logs-back:
	docker compose logs -f backend

logs-front:
	docker compose logs -f frontend

# 📊 Контейнеры
ps:
	docker compose ps

# 🌱 Сидирование
seed:
	docker compose exec backend python seed.py

# 🐚 Войти в контейнеры
bash-back:
	docker compose exec backend bash

bash-front:
	docker compose exec frontend sh