PYTHON ?= python3
DOXYGEN ?= doxygen
TEST_PATTERN ?= test_*.py
TEST_ENV ?= PYTHONDONTWRITEBYTECODE=1

.PHONY: run seed test test-unit test-integration coverage lint format doxygen docs quality

run:
	$(PYTHON) run.py

seed:
	$(PYTHON) -m app.infrastructure.demo_seed

test:
	$(TEST_ENV) $(PYTHON) -m unittest discover -s tests

test-unit:
	$(TEST_ENV) $(PYTHON) -m unittest discover -s tests/unit -p "$(TEST_PATTERN)" -v

test-integration:
	$(TEST_ENV) $(PYTHON) -m unittest discover -s tests/integration -p "$(TEST_PATTERN)" -v

coverage:
	$(PYTHON) -m coverage erase
	$(TEST_ENV) $(PYTHON) -m coverage run -m unittest discover -s tests
	$(PYTHON) -m coverage report --fail-under=80

lint:
	$(PYTHON) -m ruff check .

format:
	$(PYTHON) -m ruff format .

doxygen:
	@command -v $(DOXYGEN) >/dev/null 2>&1 || { \
		echo "Doxygen não encontrado. Instale o pacote 'doxygen' e rode novamente."; \
		exit 1; \
	}
	$(DOXYGEN) Doxyfile

docs: doxygen

quality: test coverage lint
