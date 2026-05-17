DC = docker compose -f ../docker-compose.yml

.PHONY: dev restart build logs sh install

dev:
	$(DC) up -d frontend

restart:
	$(DC) restart frontend
	$(DC) logs --tail=10 frontend

build:
	$(DC) build frontend

logs:
	$(DC) logs -f frontend

sh:
	$(DC) exec frontend sh

install:
	$(DC) exec frontend npm install $(NAME)
