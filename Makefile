# Pre-settings
.ONESHELL: # Applies to every targets in the file!
.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Default"
	@echo " - clean                  remove project cache"
	@echo ""
	@echo "CLI"
	@echo " - cli/build              build Unimake cli tool"
	@echo " - cli/install            install Unimake cli tool to user space"
	@echo " - cli/remove             remove Unimake cli tool from user space"
	@echo ""
	@echo "Python package"
	@echo " - package/build          build Python package"
	@echo " - package/publish        publish Python package to private PyPi"
	@echo ""
	@echo "Maintenance"
	@echo " - project/env/up         setup poetry environment"
	@echo " - project/env/down       destroy poetry environment"
	@echo " - project/dependencies   install project dependencies"
	@echo " - project/version        set project version from latest tag (do not call this manually)"
	@echo ""
	@echo "Development notes"
	@echo " 1) Install 'poetry' to manage the project."
	@echo "    Visit https://python-poetry.org/docs/#installation"
	@echo " 2) If you need to publish Python package to private PyPi"
	@echo "    you must put private PyPi credentials to '.env' file:"
	@echo "        PRIVATE_PYPI_URL=<url-to-private-pypi>"
	@echo "        PRIVATE_PYPI_USER=<user-name>"
	@echo "        PRIVATE_PYPI_PASSWORD=<user-password-or-token>"
	@echo " 3) Run 'make env/up'"
	@echo " 4) Run 'make dependencies/dev'"
	@echo " 5) Run 'make package/build'"
	@echo " 5) Run 'make cli/build'"
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
clean:
	@find . -type d -name "__pycache__" | xargs rm -rf {};
	@rm -rf build $(PROJECT_NAME).spec

# ################################################################################################ #
# CLI
# ################################################################################################ #

.PHONY: cli/build
cli/build: versionize
	@rm -rf dist/$(PROJECT_NAME_SHORT)
	@poetry run pyinstaller \
	--noconfirm \
	--log-level=WARN \
	--onefile \
	--nowindow \
	--hidden-import ctypes \
	--name $(PROJECT_NAME_SHORT) \
	./umk/application/main.py

.PHONY: cli/install
cli/install:
	@cp ./dist/umk ~/.local/bin/$(PROJECT_NAME_SHORT)

.PHONY: cli/remove
cli/remove:
	@rm -f ./dist/umk ~/.local/bin/$(PROJECT_NAME_SHORT)

# ################################################################################################ #
# Python package
# ################################################################################################ #

.PHONY: package/build
package/build: project/version
	poetry build

.PHONY: package/publish
package/publish: package/build
	@poetry config repositories.$(PROJECT_NAME_SHORT)-internal $(PRIVATE_PYPI_URL)
	@poetry config http-basic.$(PROJECT_NAME_SHORT)-internal $(PRIVATE_PYPI_USER) $(PRIVATE_PYPI_PASSWORD)
	@poetry publish --repository $(PROJECT_NAME_SHORT)-internal

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