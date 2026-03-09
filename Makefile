.PHONY: install fetch summarise notify run serve start test

install:
	pip install -r requirements.txt

fetch:
	python -m app.fetcher

summarise:
	python -m app.summariser

notify:
	python -m app.notifier

run:
	python -m app.pipeline

serve:
	uvicorn app.dashboard.server:app --reload --host 0.0.0.0 --port 8000

start:
	uvicorn app.dashboard.server:app --host 0.0.0.0 --port $${PORT:-8000}

test:
	python -m pytest tests/ -v
