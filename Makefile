run:
	python -m gymhero.server

docker-up-full:
	docker compose build --no-cache
	docker compose up -d --force-recreate
	alembic downgrade base && alembic upgrade head && python -m scripts.initdb --env=dev

docker-up:
	docker compose build
	docker compose up -d
	alembic downgrade base && alembic upgrade head && python -m scripts.initdb --env=dev

docker-down:
	docker compose down

docker-kill:
	docker compose kill

test-all:
	ENV=test pytest tests/

test-all-verbose:
	ENV=test pytest tests/ -s -v

test-unit:
	ENV=test pytest tests/unit/

test-integration:
	ENV=test pytest tests/integration/


cov:
	ENV=test pytest --cov-report html --cov=gymhero tests/ 

echos:
	echo $(if ${env},${env},dev)

pretty:
	isort gymhero/ && isort tests/
	black gymhero/ && black tests/

initsu:
	python -m scripts.initsu --env=$(if ${env},${env}, dev)

initdb:
	python -m scripts.initdb --env=$(if ${env},${env},dev)

initsu-test:
	python -m scripts.initdb --env=test
initdb-test:
	python -m scripts.initdb --env=test


alembic-head:
	alembic upgrade head

alembic-base:
	alembic downgrade base

alembic-up:
	alembic upgrade +1 

alembic-down:
	alembic downgrade -1

alembic-recreate:
	alembic downgrade base && alembic upgrade head

reinit:
	alembic downgrade base && alembic upgrade head && python -m scripts.initdb --env=dev

