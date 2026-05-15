PYTHON = .venv/Scripts/python.exe
COMPOSE = docker compose -f ../docker-compose.yml
EXEC = $(COMPOSE) exec backend
TEST_COMPOSE = docker compose -f ../docker-compose.test.yml

.PHONY: add install remove

venv:
	python -m venv .venv
	$(PYTHON) -m pip install pip-tools

add:
	$(PYTHON) -c "open('requirements.in', 'a').write('$(p)\n')"
	$(PYTHON) -m piptools compile requirements.in -o requirements.txt
	$(PYTHON) -m pip install -r requirements.txt
	$(EXEC) pip install $(p)

remove:
	$(PYTHON) -c "lines=open('requirements.in').readlines(); open('requirements.in','w').writelines([l for l in lines if l.strip()!='$(p)'])"
	$(PYTHON) -m piptools compile requirements.in -o requirements.txt
	$(PYTHON) -m pip uninstall $(p) -y
	$(EXEC) pip uninstall $(p) -y

install:
	$(PYTHON) -m pip install -r requirements.txt

migrate:
	$(EXEC) alembic upgrade head

downgrade:
	$(EXEC) alembic downgrade -1

makemigrations:
	$(EXEC) alembic revision --autogenerate -m "$(m)"

history:
	$(EXEC) alembic history --verbose

test-up:
	$(TEST_COMPOSE) up -d test-db --wait

test-down:
	$(TEST_COMPOSE) stop test-db
	$(TEST_COMPOSE) rm -f test-db

test:
	$(TEST_COMPOSE) exec -e TEST_DB_HOST=test-db backend python -m pytest $(args)

test-all:
	$(TEST_COMPOSE) up -d --wait && $(EXEC) python -m pytest $(args); RET=$$?; $(TEST_COMPOSE) down; exit $$RET