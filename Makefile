.PHONY: lint format typecheck check \
        test-unit test-smoke test-integration test-all \
        dev-up dev-down dev-logs dev-restart \
        clean-test clean-docker

# ---------- Code quality (local) ----------

lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run mypy .

check: lint typecheck test-unit
	@echo "✅ Lint + typecheck + unit test passed"

# ---------- Test (Testing Docker) ----------

test-unit:
	uv run pytest tests/unit -v

test-smoke:
	docker compose -f docker-compose.test.yml build test
	docker compose -f docker-compose.test.yml run --rm test pytest tests/smoke -v
	docker compose -f docker-compose.test.yml down

test-integration:
	docker compose -f docker-compose.test.yml build test
	docker compose -f docker-compose.test.yml run --rm test pytest tests/integration -v -s
	docker compose -f docker-compose.test.yml down

test-all: test-unit test-smoke test-integration
	@echo "✅ All test levels passed"

# ---------- Dev environment (Persistent Docker) ----------

dev-up:
	docker compose -f docker-compose.yml up -d

dev-down:
	docker compose -f docker-compose.yml down

dev-logs:
	docker compose -f docker-compose.yml logs -f

dev-restart: dev-down dev-up

# ---------- Cleanup ----------

clean-test:
	docker compose -f docker-compose.test.yml down -v
	docker system prune -f

clean-docker:
	@echo "⚠️  WARNING: This command will remove ALL volumes (including any local databases) and unused images!"
	@echo -n "Are you sure you want to proceed? [y/N]: " && read ans && [ "$$ans" = "y" ] || [ "$$ans" = "Y" ] || (echo "❌ Operation cancelled. No data was touched."; exit 1)
	docker system prune -a --volumes -f
	@echo "✨ Cleanup completed successfully!"
