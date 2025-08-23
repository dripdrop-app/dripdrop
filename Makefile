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

.PHONY: run-server-dev
run-server-dev:
	docker compose --profile dev up -d && uv run fastapi dev app

.PHONY: run-client-dev
run-client-dev:
	cd client && npm run dev

# Replace with celery command
# .PHONY: worker-dev
# worker-dev:
# 	infisical run --env=dev -- uv run litestar workers run --verbose --debug

.PHONY: infisical
infisical:
	infisical run --env=dev -- make $(CMD)

.PHONY: clean
clean:
	rm -rf $(shell find app -name __pycache__)
