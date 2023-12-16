FROM alpine:latest

RUN apk update && \
    apk upgrade && \
    apk add alpine-sdk linux-headers sudo

ARG USER_ID=1000
ARG USER_NAME=unimake
ARG GROUP_ID=1001
ARG GROUP_NAME=unimake
ARG SHELL=/bin/bash

COPY development/images/utils.sh /utils.sh
RUN /utils.sh user $USER_NAME $USER_ID $GROUP_NAME $GROUP_ID $SHELL
RUN sudo rm /utils.sh

USER ${USER_ID}

RUN sudo apk add git make zsh
