.PHONY: help install lint fix typecheck test cov coverage bandit audit pre-commit clean sync

# 铁则：本地一律用 uv，不直接用 pip/python
UV := uv
PY := $(UV) run python
RUV := $(UV) run

help: ## 显示可用命令
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## 安装运行+开发依赖 (uv 唯一入口)
	$(UV) sync --group dev
	$(UV) run pre-commit install

sync: ## 同步依赖 (uv.lock → .venv)
	$(UV) sync --group dev

lint: ## 只检查不修复 (CI 用)
	$(RUV) ruff check .
	$(RUV) ruff format --check .

fix: ## 一键自动修复 (本地最常用)
	$(RUV) ruff check --fix .
	$(RUV) ruff format .

typecheck: ## 类型检查
	$(RUV) mypy core main.py --ignore-missing-imports --explicit-package-bases

test: ## 跑测试 (并行)
	$(RUV) pytest -q

cov: ## 覆盖率 + 阈值 25% + 终端/HTML 报告 (阈值随覆盖率提升逐步收紧)
	$(RUV) pytest --cov --cov-report=term-missing --cov-report=html --cov-fail-under=25 -q

coverage: cov

test-fast: ## 并行测试 (xdist)
	$(RUV) pytest -q -n auto

bandit: ## 安全扫描
	$(RUV) bandit -c pyproject.toml -r core main.py

audit: ## 依赖漏洞扫描
	$(RUV) pip-audit --desc

pre-commit: ## 全量跑 pre-commit (等同 CI)
	$(RUV) pre-commit run --all-files

clean: ## 清理缓存
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

ci: lint typecheck cov bandit ## 本地一键模拟 CI 全门禁
	@echo "✅ CI gate passed"
