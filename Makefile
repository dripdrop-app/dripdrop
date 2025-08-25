CMD ?=

.PHONY: create-migration
create-migration:
	uv run alembic -c app/db/alembic.ini revision --autogenerate

.PHONY: migrate
migrate:
	uv run alembic -c app/db/alembic.ini upgrade head

.PHONY: install-server
install-server:
	uv sync && uv run pre-commit install

.PHONY: install-client
install-client:
	cd client && npm install

.PHONY: install
install: install-server install-client

.PHONY: lint
lint:
	uv run ruff check --select I --fix

.PHONY: test
test:
	ENV=testing uv run pytest tests --cov=app --cov-report=term-missing

.PHONY: test-fast
test-fast:
	ENV=testing uv run pytest tests -m "not long"

.PHONY: server-dev
server-dev:
	docker compose --profile dev up -d && uv run fastapi dev app

.PHONY: client-dev
client-dev:
	cd client && npm run dev

.PHONY: worker-dev
worker-dev:
	docker compose --profile dev up -d && uv run watchfiles "celery -A app.tasks.app worker -c 2 --loglevel=info" app/tasks

.PHONY: dev
dev:
	make server-dev & make client-dev & make worker-dev & wait

.PHONY: infisical
infisical:
	infisical run --env=dev -- make $(CMD)

.PHONY: clean
clean:
	rm -rf $(shell find app -name __pycache__) && rm -rf $(shell find client -name node_modules)

.PHONY: server
server: migrate
	uvicorn app:app --host 0.0.0.0 --port $$PORT --workers $$WORKERS

.PHONY: worker
worker: migrate
	celery -A app.tasks.app worker -c $$WORKERS --loglevel=info & celery -A app.tasks.app beat --loglevel=info & wait
