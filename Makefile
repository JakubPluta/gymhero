pretty:
	isort gymhero/ && isort tests/
	black gymhero/ && black tests/

init-superuser:
	python -m scripts.create_superuser