dev:
	docker compose build
	docker compose up -d 
	docker exec -it app alembic upgrade head
	docker exec -it app python -m scripts.initdb --env=dev

install:
	docker compose build --no-cache
	docker compose up -d --force-recreate
	docker exec -it app alembic downgrade base
	docker exec -it app alembic upgrade head
	docker exec -it app python -m scripts.initdb --env=dev

up:
	docker compose up -d

run:
	docker compose build
	docker compose up -d

initdb:
	docker exec -it app alembic downgrade base && alembic upgrade head
	docker exec -it app python -m scripts.initdb --env=dev

down:
	docker compose down

kill:
	docker compose kill

test-all:
	docker exec -it --env-file .env.test app pytest tests/

test-all-verbose:
	docker exec -it --env-file .env.test app pytest tests/ -s -vv

test-unit:
	docker exec -it --env-file .env.test app pytest tests/unit 

test-integration:
	docker exec -it --env-file .env.test app pytest tests/integration

cov-report:
	docker exec -it --env-file .env.test app pytest --cov-report html --cov=gymhero tests/ 

cov:
	docker exec -it --env-file .env.test app pytest --cov=gymhero tests/ 

pretty:
	isort gymhero/ && isort tests/
	black gymhero/ && black tests/

initsu:
	docker exec -it app python -m scripts.initsu --env=dev

alembic-head:
	docker exec -it app alembic upgrade head

alembic-base:
	docker exec -it app alembic downgrade base

alembic-up:
	docker exec -it app alembic upgrade +1

alembic-down:
	docker exec -it app alembic downgrade -1

alembic-migrate:
	docker exec -it app alembic revision --autogenerate -m "new migration"

alembic-recreate:
	docker exec -it app alembic downgrade base && alembic upgrade head
alembic-init:
	docker exec -it app alembic downgrade base && alembic upgrade head
	docker exec -it app python -m scripts.initdb --env=dev

local-run:
	python -m gymhero.server

local-recreate:
	docker compose build --no-cache
	docker compose up -d --force-recreate
	ENV=local alembic downgrade base && alembic upgrade head
	python -m scripts.initdb --env=local


get-token:
	curl -X 'POST' \
	'http://localhost:8000/auth/login' \
	-H 'accept: application/json' \
	-H 'Content-Type: application/x-www-form-urlencoded' \
	-d 'grant_type=&username=gymhero%40mail.com&password=gymhero&scope=&client_id=&client_secret='