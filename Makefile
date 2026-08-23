.PHONY: help install lint fix typecheck test cov coverage bandit audit pre-commit clean

PY := python3
PIP := pip

help: ## 显示可用命令
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## 安装运行+开发依赖
	$(PIP) install -r requirements-dev.txt
	pre-commit install

lint: ## 只检查不修复 (CI 用)
	ruff check .
	ruff format --check .

fix: ## 一键自动修复 (本地最常用)
	ruff check --fix .
	ruff format .

typecheck: ## 类型检查
	mypy core main.py --ignore-missing-imports --explicit-package-bases

test: ## 跑测试 (并行)
	pytest -q

cov: ## 覆盖率 + 阈值 25% + 终端/HTML 报告 (阈值随覆盖率提升逐步收紧)
	pytest --cov --cov-report=term-missing --cov-report=html --cov-fail-under=25 -q

coverage: cov

test-fast: ## 并行测试 (xdist)
	pytest -q -n auto

bandit: ## 安全扫描
	bandit -c pyproject.toml -r core main.py

audit: ## 依赖漏洞扫描
	pip-audit --desc

pre-commit: ## 全量跑 pre-commit (等同 CI)
	pre-commit run --all-files

clean: ## 清理缓存
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

ci: lint typecheck cov bandit ## 本地一键模拟 CI 全门禁
	@echo "✅ CI gate passed"
