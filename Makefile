.PHONY: help install lint fix typecheck test cov coverage bandit audit pre-commit clean sync

# Rule: Use uv exclusively for local development, never call pip/python directly
UV := uv
PY := $(UV) run python
RUV := $(UV) run

help: ## Display available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install runtime + development dependencies (uv entry point)
	$(UV) sync --group dev
	$(UV) run pre-commit install

sync: ## Sync dependencies (uv.lock → .venv)
	$(UV) sync --group dev

lint: ## Lint check without auto-fixing (for CI)
	$(RUV) ruff check .
	$(RUV) ruff format --check .

fix: ## One-click automatic code formatting and lint fixes
	$(RUV) ruff check --fix .
	$(RUV) ruff format .

typecheck: ## Static type checking via Mypy
	$(RUV) mypy core main.py --ignore-missing-imports --explicit-package-bases

test: ## Run test suite
	$(RUV) pytest -q

cov: ## Test coverage with >=25% threshold and HTML/terminal reports
	$(RUV) pytest --cov --cov-report=term-missing --cov-report=html --cov-fail-under=25 -q

coverage: cov

test-fast: ## Fast parallel test execution (pytest-xdist)
	$(RUV) pytest -q -n auto

bandit: ## Security vulnerability scan
	$(RUV) bandit -c pyproject.toml -r core main.py

audit: ## Dependency vulnerability audit
	$(RUV) pip-audit --desc

pre-commit: ## Run all pre-commit hooks across files
	$(RUV) pre-commit run --all-files

clean: ## Clean caches and temporary build artifacts
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage coverage.xml .hypothesis
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

update: ## Fast heuristic update of subscription matrix
	$(PY) main.py --output .

update-live: ## Full live benchmark update (Sing-box bypass validation + longevity ledger)
	$(PY) main.py --validate --output . --local

validate-dual: ## Dual-engine local validation (Sing-box + Mihomo, TUN adapter bypass)
	$(PY) validate_local.py

ci: lint typecheck cov bandit ## One-click local simulation of complete CI gate
	@echo "✅ CI gate passed"

