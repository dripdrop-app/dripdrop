.PHONY: create-migration
create-migration:
	infisical run --env=dev -- uv run alembic -c app/db/alembic.ini revision --autogenerate

.PHONY: migrate
migrate:
	infisical run --env=dev -- uv run alembic -c app/db/alembic.ini upgrade head

.PHONY: install
install:
	uv sync && uv run pre-commit install

.PHONY: lint
lint:
	ruff check --select I --fix

.PHONY: test
test:
	ENV=testing infisical run --env=dev -- uv run pytest tests

.PHONY: coverage
coverage:
	ENV=testing infisical run --env=dev -- uv run pytest --cov=app tests

.PHONY: deploy-local
deploy-local:
	docker compose --profile dev up -d 

.PHONY: run-dev
run-dev:
	infisical run --env=dev -- uv run fastapi dev app

# Replace with celery command
# .PHONY: worker-dev
# worker-dev:
# 	infisical run --env=dev -- uv run litestar workers run --verbose --debug

.PHONY: clean
clean:
	rm -rf $(shell find app -name __pycache__)
