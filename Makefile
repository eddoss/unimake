# Pre-settings
.ONESHELL: # Applies to every targets in the file!
.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Default"
	@echo " - clean                      remove project cache"
	@echo " - dependencies               install project dependencies"
	@echo " - build                      build Python package, umk and unimake"
	@echo " - install                    install Python package, umk and unimake"
	@echo " - uninstall                  uninstall Python package, umk and unimake"
	@echo ""
	@echo "Python package"
	@echo " - package/build              build Python package"
	@echo " - package/publish            publish Python package to private PyPi"
	@echo " - package/clean              remove Python package from ./dist"
	@echo " - package/install            install Python package by current pip"
	@echo " - package/uninstall          uninstall Python package by current pip"
	@echo ""
	@echo "Maintenance"
	@echo " - project/env/up             setup poetry environment"
	@echo " - project/env/down           destroy poetry environment"
	@echo " - project/dependencies       install project dependencies"
	@echo " - project/dependencies/dev   install project development dependencies"
	@echo " - project/version            set project version from latest tag (do not call this manually)"
	@echo ""
	@echo "Development notes"
	@echo " 1) Install 'poetry' to manage the project."
	@echo "    Visit https://python-poetry.org/docs/#installation"
	@echo " 2) If you need to publish Python package to private PyPi"
	@echo "    you must put private PyPi credentials to '.env' file:"
	@echo "        PRIVATE_PYPI_URL=<url-to-private-pypi>"
	@echo "        PRIVATE_PYPI_USER=<user-name>"
	@echo "        PRIVATE_PYPI_PASSWORD=<user-password-or-token>"
	@echo " 3) Run 'make project/env/up'"
	@echo " 4) Run 'make project/dependencies/dev'"
	@echo " 5) Run 'make package/build'"
	@echo " 6) Run 'make package/install'"
	@echo " 7) Call 'unimake help' or go to unimake project and call 'umk ...'"
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
#  - PRIVATE_PIPY_URL    private PyPi url
#  - PRIVATE_PIPY_USER   private PyPi user name
#  - PRIVATE_PIPY_TOKEN  private PyPi user identity token

-include $(PROJECT_ROOT)/.env


# ################################################################################################ #
# Default
# ################################################################################################ #

.PHONY: clean
clean: package/clean
	@find . -type d -name "__pycache__" | xargs rm -rf {};
	@rm -rf build
	@rm -f ./$(PROJECT_NAME).spec
	@rm -f ./$(PROJECT_NAME_SHORT).spec

.PHONY: dependencies
dependencies: project/dependencies

.PHONY: build
build: package/build

.PHONY: install
install: package/build package/install

.PHONY: uninstall
uninstall: package/uninstall

# ################################################################################################ #
# Python package
# ################################################################################################ #

.PHONY: package/clean
package/clean:
	@rm -f ./dist/umk-*

.PHONY: package/build
package/build: package/clean project/version
	poetry build

.PHONY: package/publish
package/publish: package/build
	@poetry config repositories.$(PROJECT_NAME_SHORT)-internal $(PRIVATE_PYPI_URL)
	@poetry config http-basic.$(PROJECT_NAME_SHORT)-internal $(PRIVATE_PYPI_USER) $(PRIVATE_PYPI_PASSWORD)
	@poetry publish --repository $(PROJECT_NAME_SHORT)-internal

.PHONY: package/install
package/install: package/uninstall
	@pip install ./dist/$(PROJECT_NAME_SHORT)-*.whl

.PHONY: package/uninstall
package/uninstall:
	@pip uninstall --yes umk

# ################################################################################################ #
# Maintenance
# ################################################################################################ #

.PHONY: project/env/up
project/env/up:
	@poetry env use -n -- $(shell which python3)

.PHONY: project/env/down
project/env/down:
	@rm -rf .venv

.PHONY: project/dependencies
project/dependencies:
	@poetry install

.PHONY: project/dependencies/dev
project/dependencies/dev:
	@poetry install --with=dev

.PHONY: project/version
project/version:
	@sed -i 's/version = ".*"/version = "$(PROJECT_VERSION_RAW)"/' $(PROJECT_ROOT)/pyproject.toml

.PHONY: project/format
project/format:
	@echo "Format umk"
	@poetry run black $(PROJECT_ROOT)/umk
	@echo "Format unimake"
	@poetry run black $(PROJECT_ROOT)/unimake
