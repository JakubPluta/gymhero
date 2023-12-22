recreate:
	docker compose build --no-cache
	docker compose up -d --force-recreate
	docker exec -it app alembic downgrade base && alembic upgrade head
	docker exec -it app python -m scripts.initdb --env=dev

up:
	docker compose build
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
	docker exec -it --env-file .env.test app pip install pytest pytest-cov pytest-mock
	docker exec -it --env-file .env.test app pytest tests/ -s -vv

test-all-verbose:
	ENV=local pytest tests/ -s -vv

test-unit:
	ENV=test pytest tests/unit/

test-integration:
	ENV=test pytest tests/integration/

cov:
	ENV=test pytest --cov-report html --cov=gymhero tests/ 


pretty:
	isort gymhero/ && isort tests/
	black gymhero/ && black tests/

initsu:
	docker exec -it app python -m scripts.initsu --env=dev

initdb:
	docker exec -it app python -m scripts.initdb --env=dev

ah:
	docker exec -it app alembic upgrade head

ab:
	docker exec -it app alembic downgrade base

aup:
	docker exec -it app alembic upgrade +1

aup:
	docker exec -it app alembic downgrade -1

arc:
	docker exec -it app alembic downgrade base && alembic upgrade head
ari:
	docker exec -it app alembic downgrade base && alembic upgrade head
	docker exec -it app python -m scripts.initdb --env=dev

local-run:
	python -m gymhero.server

local-recreate:
	docker compose build --no-cache
	docker compose up -d --force-recreate
	ENV=local alembic downgrade base && alembic upgrade head
	python -m scripts.initdb --env=local