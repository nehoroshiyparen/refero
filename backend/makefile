PYTHON = .venv/Scripts/python.exe
COMPOSE = docker compose -f ../docker-compose.yml
EXEC = $(COMPOSE) exec backend

.PHONY: add install

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