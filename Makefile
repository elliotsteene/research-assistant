notebook:
	@poetry run python -m jupyter notebook

run:
	@poetry run python report_agent/main.py

install:
	@poetry install
