run:
	python -m gymhero.server

docker-up:
	docker compose build
	docker compose up -d --force-recreate
	alembic -n dev downgrade base && alembic -n dev upgrade head && python -m scripts.initdb --env=dev

docker-up-test:
	docker compose build
	docker compose up -d --force-recreate
	alembic -n test downgrade base && alembic -n test upgrade head && python -m scripts.initdb --env=test

docker-up-full:
	docker compose build --no-cache
	docker compose up -d --force-recreate
	alembic -n dev downgrade base && alembic -n dev upgrade head && python -m scripts.initdb --env=dev
	alembic -n test downgrade base && alembic -n test upgrade head && python -m scripts.initdb --env=test

docker-down:
	docker compose down

docker-kill:
	docker compose kill

test-all:
	ENV=test pytest tests/ -s -v 

test-unit:
	ENV=test pytest tests/unit/ -s -v

test-integration:
	ENV=test pytest tests/integration/ -s -v


cov:
	ENV=test pytest --cov=gymhero tests/

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
	alembic -n dev upgrade head

alembic-base:
	alembic -n dev downgrade base

alembic-up:
	alembic -n dev upgrade +1 

alembic-down:
	alembic -n dev downgrade -1

alembic-recreate:
	alembic -n dev downgrade base && alembic -n dev upgrade head


alembic-head-test:
	alembic -n test upgrade head

alembic-base-test:
	alembic -n test downgrade base

alembic-up-test:
	alembic -n test upgrade +1 

alembic-down-test:
	alembic -n test downgrade -1

alembic-recreate-test:
	alembic -n test downgrade base && alembic -n test upgrade head

reinit:
	alembic -n dev downgrade base && alembic -n dev upgrade head && python -m scripts.initdb --env=dev

reinit-test:
	alembic -n test downgrade base && alembic -n test upgrade head && python -m scripts.initdb --env=test


