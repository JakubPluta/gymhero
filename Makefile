run:
	python -m gymhero.server

install:
	docker compose build
	docker compose up -d --force-recreate
	alembic downgrade base && alembic upgrade head && python -m scripts.initdb --env=dev

test-all:
	pytest tests/

pretty:
	isort gymhero/ && isort tests/
	black gymhero/ && black tests/

initsu:
	python -m scripts.initsu

initdb:
	python -m scripts.initdb --env=dev

initdb-test:
	python -m scripts.initdb --env=test

alembic-head:
	echo "alembic upgrade head"
	alembic upgrade head

alembic-base:
	echo "alembic downgrade base"
	alembic downgrade base

alembic-up:
	alembic upgrade +1 

alembic-down:
	alembic downgrade -1

alembic-recreate:
	alembic downgrade base && alembic upgrade head

alembic-recreate-init:
	alembic downgrade base && alembic upgrade head && python -m scripts.initdb --env=dev

arci:
	alembic downgrade base && alembic upgrade head && python -m scripts.initdb --env=dev

arc:
	alembic downgrade base && alembic upgrade head

ah:
	alembic upgrade head
ab:
	alembic downgrade base


