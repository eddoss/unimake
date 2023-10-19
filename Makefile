# Pre-settings
.ONESHELL: # Applies to every targets in the file!
.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "NOTE: install 'poetry' to manage the project."
	@echo "      Visit https://python-poetry.org/docs/#installation"
	@echo ""
	@echo "Check the Makefile to know exactly what each target is doing."


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
#                                       AHTUNG SECTION BEGIN
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #

# Its super important to export varibles below.

export PROJECT_NAME           := unimake
export PROJECT_NAME_SHORT     := umk
export PROJECT_ROOT           := $(CURDIR)
export PROJECT_VERSION        := $(shell git describe --abbrev=0 --tags)
export PROJECT_VERSION_RAW    := $(subst v,,$(PROJECT_VERSION))

# Private artifactory attributes will be loaded from .env
#  - ARTIFACTORY_USER   artifactory user name
#  - ARTIFACTORY_TOKEN  artifactory user identity token
-include $(PROJECT_ROOT)/.env


# ################################################################################################ #
# Default
# ################################################################################################ #

.PHONY: clean
clean:
	@find . -type d -name "__pycache__" | xargs rm -rf {};
	@rm -rf build $(PROJECT_NAME).spec

.PHONY: build
build:
	@rm -rf dist/$(PROJECT_NAME_SHORT)
	@poetry run pyinstaller \
	--noconfirm \
	--log-level=WARN \
	--onefile \
    --nowindow \
    --hidden-import ctypes \
    --name $(PROJECT_NAME_SHORT) \
    ./umk/application/main.py

.PHONY: package
package:
	poetry build

.PHONY: publish
publish:
	@poetry config repositories.internal $(PRIVATE_PYPI_URL)
	@poetry config http-basic.internal $(PRIVATE_PYPI_USER) $(PRIVATE_PYPI_PASSWORD)
	@poetry build
	@poetry publish --repository internal

# ################################################################################################ #
# Maintenance
# ################################################################################################ #

.PHONY: env/up
env/up:
	@poetry env use -n -- $(shell which python3)

.PHONY: env/down
env/down:
	@rm -rf .venv

.PHONY: dependencies
dependencies:
	@poetry install --with=dev

.PHONY: setver
setver:
	@sed -i 's/version = ".*"/version = "$(PROJECT_VERSION_RAW)"/' $(PROJECT_ROOT)/pyproject.toml