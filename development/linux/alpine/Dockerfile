ARG OS_VERSION=latest
FROM alpine:$OS_VERSION

ARG USER_ID=1000
ARG USER_NAME=unimake
ARG GROUP_ID=1001
ARG GROUP_NAME=unimake
ARG SHELL=/bin/bash

RUN apk update && \
    apk upgrade && \
    apk add alpine-sdk linux-headers sudo

COPY development/linux/user.sh /create_user.sh
RUN /create_user.sh alpine $USER_NAME $USER_ID $GROUP_NAME $GROUP_ID $SHELL
RUN sudo rm /create_user.sh

USER ${USER_ID}
