ROOT := $(shell pwd)
SYSTEM := $(shell uname -s)

VENV := venv
ACTIVATE := . $(VENV)/bin/activate;
DEACTIVATE := deactivate;

MANIFEST_IGNORE := .pylintrc-relaxed,Makefile,MANIFEST.in,OSSMETADATA,RELEASE_PROCESS.md,tests*,tests/**,tox.ini

## help: print this help message
.PHONY: help
help:
	@echo 'Usage:'
	@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':' |  sed -e 's/^/ /'

## all: clean test lint check-manifest
.PHONY: all
all: clean test lint check-manifest

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
	rm -rf .coverage htmlcov netflix_spectator_py.egg-info
	find spectator tests -name __pycache__ -prune -exec rm -rf {} \;

## test: run tests with coverage enabled
.PHONY: test
test:
ifeq ($(SYSTEM), Darwin)
	$(ACTIVATE) pytest --cov=spectator tests
else
	pytest --cov=spectator tests
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

## lint: run pylint on the project
.PHONY: lint
lint:
ifeq ($(SYSTEM), Darwin)
	$(ACTIVATE) pylint --rcfile=.pylintrc-relaxed spectator tests
else
	pylint --rcfile=.pylintrc-relaxed spectator tests
endif

## check-manifest: validate the manifest file
.PHONY: check-manifest
check-manifest:
ifeq ($(SYSTEM), Darwin)
	$(ACTIVATE) check-manifest --ignore $(MANIFEST_IGNORE)
	@echo
	$(ACTIVATE) python setup.py check --metadata --strict
else
	check-manifest --ignore $(MANIFEST_IGNORE)
	@echo
	python setup.py check --metadata --strict
endif

# DEBUG: print out a a variable via `make print-FOO`
print-%: ; @echo $* = $($*)
