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

export PROJECT_NAME       := Unimake
export PROJECT_NAME_SHORT := umk
export PROJECT_ROOT       := $(CURDIR)

# Private artifactory attributes will be loaded from .env
#  - ARTIFACTORY_USER   artifactory user name
#  - ARTIFACTORY_TOKEN  artifactory user identity token
include $(PROJECT_ROOT)/.env


# ################################################################################################ #
# Default
# ################################################################################################ #

.PHONY: clean
clean:
	@find . -type d -name "__pycache__" | xargs rm -rf {};
	@rm -rf build $(PROJECT_NAME_SHORT).spec

.PHONY: build
build:
	@rm -rf dist
	@pyinstaller \
	--noconfirm \
	--log-level=WARN \
	--onefile \
    --nowindow \
    --hidden-import ctypes \
    --name $(PROJECT_NAME_SHORT) \
    ./umk/application/main.py

# ################################################################################################ #
# Project
# ################################################################################################ #

.PHONY: dependencies
dependencies:
	@poetry install

# ################################################################################################ #
# Maintenance
# ################################################################################################ #

.PHONY: env/up
env/up:
	@poetry env use -n -- $(shell which python3)

.PHONY: env/down
env/down:
	@rm -rf .venv

.PHONY: publish
publish:
	@poetry config repositories.internal $(ARTIFACTORY_URL)
	@poetry config http-basic.internal $(ARTIFACTORY_USER) $(ARTIFACTORY_TOKEN)
	@poetry build
	@poetry publish --repository inter
