ARG OS_VERSION=latest
FROM ubuntu:$OS_VERSION

ARG USER_ID=1000
ARG USER_NAME=unimake
ARG GROUP_ID=1001
ARG GROUP_NAME=unimake
ARG SHELL=/bin/bash

RUN apt update && apt -y install sudo

COPY user.sh /create_user.sh
RUN /create_user.sh $USER_NAME $USER_ID $GROUP_NAME $GROUP_ID $SHELL
RUN sudo rm /create_user.sh

USER ${USER_ID}
