FROM ubuntu:latest

RUN apt update && apt install -y openssh-server openssh-client openssh-sftp-server sudo
RUN useradd -rm -d /home/unimake -s /bin/sh -g root -G sudo -u 1000 unimake
RUN echo 'unimake:unimake' | chpasswd
RUN service ssh restart

ENTRYPOINT ["/usr/sbin/sshd","-D"]