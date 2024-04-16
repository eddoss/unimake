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

# ################################################################################################ #
# Global variables
# ################################################################################################ #

# Project
# ................................................................................................ #
export PROJECT_NAME           := unimake
export PROJECT_NAME_SHORT     := umk
export PROJECT_ROOT           := $(CURDIR)
export PROJECT_TESTS          := $(PROJECT_ROOT)/tests
export PROJECT_DEVELOPMENT    := $(PROJECT_ROOT)/development
export PROJECT_VERSION        := $(shell git describe --abbrev=0 --tags)
export PROJECT_VERSION_RAW    := $(subst v,,$(PROJECT_VERSION))
export PY                     ?= python

# Development docker images
# ................................................................................................ #
export IMAGE            := dev.$(PROJECT_NAME)
export IMAGE_DEV_BASE   := $(IMAGE).base
export IMAGE_DEV_GOLANG := $(IMAGE).base

export IMAGE__BASE   := $(IMAGE).base

# Secure variables from .env
# ................................................................................................ #
-include $(PROJECT_ROOT)/.env

# Private artifactory attributes will be loaded from .env
#  - PRIVATE_PIPY_URL    private PyPi url
#  - PRIVATE_PIPY_USER   private PyPi user name
#  - PRIVATE_PIPY_TOKEN  private PyPi user identity token


# ################################################################################################ #
# Default
# ################################################################################################ #

.PHONY: clean
clean: package/clean
	find . -type f -name "*.py[co]" -delete -or -type d -name "__pycache__" -delete
	@#find . -type d -name "__pycache__" | xargs rm -rf {};
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

.PHONY: dev/up
dev/up: dev/down dev/image dev/image/golang remote/ssh remote/container

.PHONY: dev/down
dev/down: remote/ssh/stop remote/container/stop dev/image/destroy

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
	@poetry env use -n -- $(shell which $(PY))

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

# ################################################################################################ #
# Development
# ################################################################################################ #

export DEV_IMAGE_BASE   := dev.$(PROJECT_NAME).base
export DEV_IMAGE_GOLANG := dev.$(PROJECT_NAME).golang

.PHONY: dev/image
dev/image: dev/image/base dev/image/golang

.PHONY: dev/image/destroy
dev/image/destroy: dev/image/base/destroy dev/image/golang/destroy

.PHONY: dev/image/base
dev/image/base: dev/image/base/destroy
	@docker build \
		--tag $(DEV_IMAGE_BASE) \
		--build-arg USER_ID=$(shell id -u) \
		--build-arg USER_NAME=$(USER) \
		--build-arg GROUP_ID=$(shell id -g) \
		--build-arg GROUP_NAME=$(USER) \
		--file $(PROJECT_DEVELOPMENT)/images/base.dockerfile $(PROJECT_ROOT)

.PHONY: dev/image/base/destroy
dev/image/base/destroy:
	@docker image ls -q --filter "reference=$(DEV_IMAGE_BASE)" | grep -q . && docker image rm -f $(DEV_IMAGE_BASE) || true

.PHONY: dev/image/golang
dev/image/golang: dev/image/golang/destroy
	@docker build \
		--tag $(DEV_IMAGE_GOLANG) \
		--build-arg BASE=$(DEV_IMAGE_BASE) \
		--file $(PROJECT_DEVELOPMENT)/images/golang.dockerfile $(PROJECT_ROOT)

.PHONY: dev/image/golang/destroy
dev/image/golang/destroy:
	@docker image ls -q --filter "reference=$(DEV_IMAGE_GOLANG)" | grep -q . && docker image rm -f $(DEV_IMAGE_GOLANG) || true

# ################################################################################################ #
# Development remotes
# ################################################################################################ #

export REMOTES_IMAGE_NAME := dev.$(PROJECT_NAME).remotes

.PHONY: remote/ssh
remote/ssh: remote/ssh/stop
	@docker compose -f $(PROJECT_DEVELOPMENT)/remotes/ssh/docker-compose.yaml up -d --build
	@docker compose exec $(REMOTES_IMAGE_NAME).ssh make install
	@echo 'SSH remote environment run in container "dev.unimake.ssh"'
	@echo " - ip:   171.16.14.2"
	@echo " - port: 22"
	@echo " - user: unimake"
	@echo " - pass: unimake"

.PHONY: remote/ssh/stop
remote/ssh/stop:
	@docker compose -f $(PROJECT_DEVELOPMENT)/remotes/ssh/docker-compose.yaml down --remove-orphans --rmi all

.PHONY: remote/container
remote/container: remote/container/stop
	@echo "Build 'remotes/container' image"
	@docker build \
		--tag dev.$(REMOTES_IMAGE_NAME).container \
		--file $(PROJECT_DEVELOPMENT)/remotes/container/Dockerfile \
		$(PROJECT_ROOT)
	@echo "Create 'remotes/container' container"
	@docker container create \
		--name $(REMOTES_IMAGE_NAME).container \
		--volume="$(PROJECT_ROOT):/home/$(USER)/workdir" \
		--workdir /home/$(USER)/workdir \
		--user "$(shell id -u):$(shell id -g)" \
		$(REMOTES_IMAGE_NAME).container
	@docker exec $(REMOTES_IMAGE_NAME).container make install
	@echo "Container remote environment is created"
	@echo " - image:     $(REMOTES_IMAGE_NAME).container"
	@echo " - container: $(REMOTES_IMAGE_NAME).container"

.PHONY: remote/container/stop
remote/container/stop:
	@docker container ls -a -q --filter "name=$(REMOTES_IMAGE_NAME).container" | grep -q . && docker container rm -f $(REMOTES_IMAGE_NAME).container || true
