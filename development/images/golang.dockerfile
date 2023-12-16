ARG BASE
FROM $BASE

RUN sudo apk add go && \
    go install github.com/go-delve/delve/cmd/dlv@latest && \
    sudo cp ~/go/bin/dlv /usr/bin/dlv
