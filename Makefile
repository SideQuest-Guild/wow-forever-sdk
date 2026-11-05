.DEFAULT_GOAL := help
UV ?= uv

help: ## Display this help text
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

# =============================================================================
# Environment State
# =============================================================================

.state/synced: pyproject.toml uv.lock
	$(UV) sync --locked
	mkdir -p .state && touch .state/synced

# =============================================================================
# Setup
# =============================================================================

##@ Setup

install: .state/synced ## Create the virtualenv with every dependency group

hooks: .state/synced ## Install the prek git hooks
	$(UV) run --locked prek install

upgrade: ## Upgrade locked dependencies and hook revisions
	$(UV) lock --upgrade
	$(UV) run prek autoupdate
	rm -f .state/synced

clean: docs-clean ## Remove the virtualenv, caches and build output
	rm -rf .state .venv dist htmlcov .coverage .pytest_cache .ruff_cache

# =============================================================================
# Development
# =============================================================================

##@ Development

generate: .state/synced ## Regenerate src/wow/_sync from src/wow/_async
	$(UV) run --locked scripts/unasync.py

fixtures: .state/synced ## Re-record tests/fixtures from the live API (needs BATTLENET_CLIENT_ID/SECRET)
	$(UV) run --locked scripts/record_fixtures.py

# =============================================================================
# Code Quality
# =============================================================================

##@ Code Quality

lint: .state/synced ## Run ruff linter (--fix enabled)
	$(UV) run --locked ruff check --fix

fmt: .state/synced ## Format Python and pyproject.toml
	$(UV) run --locked ruff format
	@# pyproject-fmt exits 1 after edits; check again to distinguish edits from errors.
	$(UV) run --locked pyproject-fmt pyproject.toml || $(UV) run --locked pyproject-fmt --check pyproject.toml

type-check: .state/synced ## Type-check with pyrefly against the baseline
	$(UV) run --locked pyrefly check

type-baseline: .state/synced ## Accept current pyrefly errors into pyrefly-baseline.json
	$(UV) run --locked pyrefly check --update-baseline

check: .state/synced ## Verify lint, format, spelling, generated code, types and workflows without changing files
	$(UV) run --locked ruff check
	$(UV) run --locked ruff format --check
	$(UV) run --locked pyproject-fmt --check pyproject.toml
	$(UV) run --locked codespell
	$(UV) run --locked scripts/unasync.py --check
	$(UV) run --locked pyrefly check
	$(UV) run --locked zizmor --offline .github/

# =============================================================================
# Testing
# =============================================================================

##@ Testing

test: .state/synced ## Run the test suite; fails below 100% branch coverage
	$(UV) run --locked pytest --cov

coverage: .state/synced ## Run the test suite and open an HTML coverage report
	$(UV) run --locked pytest --cov --cov-report=html
	@echo "=> htmlcov/index.html"

# =============================================================================
# Documentation
# =============================================================================

##@ Documentation

DOCS_BUILDDIR ?= docs/_build
DOCS_PORT ?= 8001

docs: docs-clean .state/synced ## Build documentation, failing on warnings
	$(UV) run --locked sphinx-build -M html docs "$(DOCS_BUILDDIR)" -E -a -j auto --keep-going -W

docs-serve: docs-clean .state/synced ## Serve documentation with live reload
	$(UV) run --locked sphinx-autobuild docs "$(DOCS_BUILDDIR)/html" -j auto --port "$(DOCS_PORT)" --keep-going -W

docs-clean: ## Clean built documentation
	rm -rf "$(DOCS_BUILDDIR)"

# =============================================================================
# Release
# =============================================================================

##@ Release

build: .state/synced ## Build the sdist and wheel into dist/
	rm -rf dist
	$(UV) build

ci: check test docs build ## Run everything CI runs

.PHONY: help install hooks upgrade clean
.PHONY: generate fixtures
.PHONY: lint fmt type-check type-baseline check
.PHONY: test coverage
.PHONY: docs docs-serve docs-clean
.PHONY: build ci
