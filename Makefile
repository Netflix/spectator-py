ROOT := $(shell pwd)
SYSTEM := $(shell uname -s)

VENV := venv
ACTIVATE := . $(VENV)/bin/activate;

MANIFEST_IGNORE := .pylintrc-relaxed,Makefile,MANIFEST.in,OSSMETADATA,RELEASE_PROCESS.md,tests*,tests/**,tox.ini


.PHONY: all
all: clean test lint check-manifest

.PHONY: setup-venv
setup-venv:
	python3 -m venv venv
	$(ACTIVATE) pip3 install --upgrade pip
	$(ACTIVATE) pip3 install -e ".[dev]"

.PHONY: remove-venv
remove-venv:
	rm -rf venv

.PHONY: install-deps
install-deps:
ifeq ($(SYSTEM), Darwin)
	$(ACTIVATE) pip3 install --upgrade pip
	$(ACTIVATE) pip3 install -e ".[dev]"
else
	pip3 install --upgrade pip
	pip3 install -e ".[dev]"
endif

.PHONY: clean
clean:
	rm -rf .coverage htmlcov netflix_spectator_py.egg-info
	find spectator tests -name __pycache__ -prune -exec rm -rf {} \;

.PHONY: test
test:
ifeq ($(SYSTEM), Darwin)
	$(ACTIVATE) pytest --cov=spectator tests
else
	pytest --cov=spectator tests
endif

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

.PHONY: lint
lint:
ifeq ($(SYSTEM), Darwin)
	$(ACTIVATE) pylint --rcfile=.pylintrc-relaxed spectator tests
else
	pylint --rcfile=.pylintrc-relaxed spectator tests
endif

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
