FROM ubuntu:latest

RUN apt update && apt install -y openssh-server openssh-client openssh-sftp-server sudo
RUN groupadd -g 1006 umk
RUN useradd -rm -d /home/unimake -s /bin/sh -g umk -G sudo -u 1005 unimake
RUN #useradd -rm -d /home/unimake -s /bin/sh -u 1005 unimake
RUN echo 'unimake:unimake' | chpasswd
RUN service ssh restart

ENTRYPOINT ["/usr/sbin/sshd","-D"]