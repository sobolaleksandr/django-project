.PHONY: install migrate run superuser seed test cov lint format up down

install:
	python -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements-dev.txt
	cp -n .env.example .env || true

migrate:
	.venv/bin/python manage.py migrate

run:
	.venv/bin/python manage.py runserver

superuser:
	.venv/bin/python manage.py createsuperuser

seed:
	.venv/bin/python manage.py seed_demo

test:
	.venv/bin/pytest

cov:
	.venv/bin/pytest --cov --cov-report=term-missing

lint:
	.venv/bin/ruff check .
	.venv/bin/ruff format --check .

format:
	.venv/bin/ruff check --fix .
	.venv/bin/ruff format .

up:
	docker compose up --build

down:
	docker compose down -v
