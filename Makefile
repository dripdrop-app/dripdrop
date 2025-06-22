CMD ?=

.PHONY: create-migration
create-migration:
	uv run alembic -c app/db/alembic.ini revision --autogenerate

.PHONY: migrate
migrate:
	uv run alembic -c app/db/alembic.ini upgrade head

.PHONY: install
install:
	uv sync && uv run pre-commit install

.PHONY: lint
lint:
	uv run ruff check --select I --fix

.PHONY: test
test:
	ENV=testing uv run pytest tests

.PHONY: coverage
coverage:
	ENV=testing uv run pytest --cov=app tests

.PHONY: run-dev
run-dev:
	docker compose --profile dev up -d && uv run fastapi dev app

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
