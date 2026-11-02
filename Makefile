ROOT := $(shell pwd)
SYSTEM := $(shell uname -s)

VENV := venv
ACTIVATE := . $(VENV)/bin/activate;
DEACTIVATE := deactivate;

## help: print this help message
.PHONY: help
help:
	@echo 'Usage:'
	@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':' |  sed -e 's/^/ /'

## all: clean test lint typecheck check-manifest
.PHONY: all
all: clean test lint typecheck check-manifest

## setup-venv: create new virtualenv with dev dependencies
.PHONY: setup-venv
setup-venv:
	python3 -m venv venv
	$(ACTIVATE) pip3 install --upgrade pip
	$(ACTIVATE) pip3 install -e ".[dev]"

## remove-venv: remove virtualenv
.PHONY: remove-venv
remove-venv:
	rm -rf venv

## install-deps: install dependencies into the venv
.PHONY: install-deps
install-deps:
ifeq ($(SYSTEM), Darwin)
	$(ACTIVATE) pip3 install --upgrade pip
	$(ACTIVATE) pip3 install -e ".[dev]"
else
	pip3 install --upgrade pip
	pip3 install -e ".[dev]"
endif

## clean: cleanup the project
.PHONY: clean
clean:
	rm -rf .coverage build dist htmlcov netflix_spectator_py.egg-info
	find spectator tests -name __pycache__ -prune -exec rm -rf {} \;

## test: run tests with coverage enabled
.PHONY: test
test:
ifeq ($(SYSTEM), Darwin)
	$(ACTIVATE) pytest --cov=spectator tests
else
	pytest --cov=spectator tests
endif

## lint: run the ruff linter and check formatting
.PHONY: lint
lint:
ifeq ($(SYSTEM), Darwin)
	$(ACTIVATE) ruff check .
	$(ACTIVATE) ruff format --check .
else
	ruff check .
	ruff format --check .
endif

## format: apply ruff lint fixes and formatting
.PHONY: format
format:
ifeq ($(SYSTEM), Darwin)
	$(ACTIVATE) ruff check --fix .
	$(ACTIVATE) ruff format .
else
	ruff check --fix .
	ruff format .
endif

## typecheck: run mypy on the project
.PHONY: typecheck
typecheck:
ifeq ($(SYSTEM), Darwin)
	$(ACTIVATE) mypy spectator tests
else
	mypy spectator tests
endif

## check-manifest: validate the manifest file and the built distributions
.PHONY: check-manifest
check-manifest:
	rm -rf dist
ifeq ($(SYSTEM), Darwin)
	$(ACTIVATE) check-manifest
	@echo
	$(ACTIVATE) python -m build --outdir dist .
	$(ACTIVATE) twine check --strict dist/*
else
	check-manifest
	@echo
	python -m build --outdir dist .
	twine check --strict dist/*
endif

## coverage: produce a coverage report
.PHONY: coverage
coverage: .coverage
ifeq ($(SYSTEM), Darwin)
	$(ACTIVATE) coverage report -m
	@echo
	$(ACTIVATE) coverage html
	@echo
	open htmlcov/index.html
else
	coverage report -m
	@echo
	coverage html
endif

# DEBUG: print out a a variable via `make print-FOO`
print-%: ; @echo $* = $($*)
