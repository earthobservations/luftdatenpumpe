# ============
# Main targets
# ============


# -------------
# Configuration
# -------------

$(eval venvpath     := .venv)
$(eval pip          := $(venvpath)/bin/pip)
$(eval python       := $(venvpath)/bin/python)
$(eval pytest       := $(venvpath)/bin/pytest)
$(eval bumpversion  := $(venvpath)/bin/bumpversion)
$(eval twine        := $(venvpath)/bin/twine)
$(eval sphinx       := $(venvpath)/bin/sphinx-build)
$(eval coverage     := $(venvpath)/bin/coverage)
$(eval black        := $(venvpath)/bin/black)
$(eval isort        := $(venvpath)/bin/isort)
$(eval proselint    := $(venvpath)/bin/proselint)
$(eval poe          := $(venvpath)/bin/poe)


# Setup Python virtualenv
setup-virtualenv:
	@test -e $(python) || python3 -m venv $(venvpath)
	$(pip) install --requirement=requirements-utils.txt


# -------
# Testing
# -------

# Run the main test suite
test:
	@test -e $(pytest) || $(MAKE) install-tests
	@$(pytest) tests -m 'not slow' --show-capture=all --verbose

test-refresh: install-tests test

test-junit: install-tests
	@$(pytest) tests --junit-xml .pytest_results/pytest.xml

test-coverage: install-tests
	@$(pytest) tests \
		--junit-xml .pytest_results/pytest.xml \
		--cov luftdatenpumpe \
		--cov-report term-missing \
		--cov-report html:.pytest_results/htmlcov \
		--cov-report xml:.pytest_results/coverage.xml

# -------
# Release
# -------

# Release this piece of software
# Synopsis:
#   make release bump=minor  (major,minor,patch)
release: bumpversion push build upload


# -------------
# Documentation
# -------------

# Build the documentation
docs-html: install-doctools
	touch doc/index.rst
	export SPHINXBUILD="`pwd`/$(sphinx)"; cd doc; make html


# ===============
# Utility targets
# ===============
bumpversion: install-releasetools
	@$(bumpversion) $(bump)

push:
	git push && git push --tags

build:
	@$(python) -m build

upload:
	$(twine) upload --skip-existing dist/*{.tar.gz,.whl}

install-doctools: setup-virtualenv
	@$(pip) install --quiet --requirement requirements-docs.txt --upgrade

install-releasetools: setup-virtualenv
	@$(pip) install --quiet --requirement requirements-release.txt --upgrade

install-tests: setup-virtualenv
	@$(pip) install --upgrade --editable .[test]
	@touch $(venvpath)/bin/activate
	@mkdir -p .pytest_results


# ----------------------
# Formatting and linting
# ----------------------

format: setup-virtualenv
	$(poe) format

lint: setup-virtualenv
	$(poe) lint


# -------
# Project
# -------

mkvar:
	mkdir -p var/lib

redis-start: mkvar
	docker run --rm -it --publish 6379:6379 redis:7

postgis-start:
	docker run --rm -it --publish=5432:5432 --env "POSTGRES_HOST_AUTH_METHOD=trust" postgis/postgis:14-3.3

influxdb-start:
	docker run --rm -it --publish=8086:8086 influxdb:1.8

mosquitto-start:
	docker run --rm -it --publish=1883:1883 eclipse-mosquitto:2.0.15 mosquitto -c /mosquitto-no-auth.conf

grafana-start:
	docker run --rm -it --publish=3000:3000 --env='GF_SECURITY_ADMIN_PASSWORD=admin' grafana/grafana:8.5.15
