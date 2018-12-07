# ============
# Main targets
# ============


# -------------
# Configuration
# -------------

$(eval venvpath     := .venv_util)
$(eval pip          := $(venvpath)/bin/pip)
$(eval python       := $(venvpath)/bin/python)
$(eval pytest       := $(venvpath)/bin/pytest)

# Setup Python virtualenv
setup-virtualenv:
	@test -e $(python) || `command -v virtualenv` --python=python3 --no-site-packages $(venvpath)


# -------
# Testing
# -------

# Run the main test suite
test:
	@test -e $(pytest) || $(MAKE) install-tests
	@$(pytest) tests -m 'not slow'

test-refresh: install-tests test

test-junit: install-tests
	@$(pytest) tests --junit-xml .pytest_results/pytest.xml

test-coverage: install-tests
	@$(pytest) tests \
		--junit-xml .pytest_results/pytest.xml \
		--cov mqttwarn --cov-branch \
		--cov-report term-missing \
		--cov-report html:.pytest_results/htmlcov \
		--cov-report xml:.pytest_results/coverage.xml

# ===============
# Utility targets
# ===============
install-tests: setup-virtualenv
	@$(pip) install --quiet --editable .[test] --upgrade
	@$(python) setup.py --quiet develop
	@touch $(venvpath)/bin/activate
	@mkdir -p .pytest_results



# -------
# Project
# -------

mkvar:
	mkdir -p var/lib

redis-start: mkvar
	echo 'dir ./var/lib\nappendonly yes' | redis-server -

postgis-start:
	pg_ctl -D /usr/local/var/postgres start
