.PHONY: start test stop load-test

start:
	docker-compose up --build

stop:
	docker-compose down

test:
	# Create virtual environment if not exists
	test -d .venv || python -m venv .venv
	# Activate virtual environment and install requirements
	. .venv/bin/activate && pip install -r requirements_test.txt
	# Run pytest
	. .venv/bin/activate && python -m pytest

load-test:
	# Start the server in the background
	docker-compose up --build -d

	# Create virtual environment if not exists
	test -d .venv || python -m venv .venv

	# Activate virtual environment and install requirements and locust
	. .venv/bin/activate && pip install -r requirements.txt locust

	# Run Locust
	. .venv/bin/activate && locust -f locustfile.py

	# Optionally, stop the server after testing
	# make stop