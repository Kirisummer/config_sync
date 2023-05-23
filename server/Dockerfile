FROM ubuntu:20.04

# setup env 
ARG OWNER_USER
ARG OWNER_GRP
ARG ADMIN_GRP
ARG USER_GRP

ENV ROOT_DIR=/config-server
ENV CMD_DIR=${ROOT_DIR}/scripts
ENV REPO_DIR=${ROOT_DIR}/repos
ENV USER_DIR=${ROOT_DIR}/users
ENV PASSWD_DIR=${ROOT_DIR}/passwd

ENV OWNER_USER=${OWNER_USER}
ENV OWNER_GRP=${OWNER_GRP}
ENV ADMIN_GRP=${ADMIN_GRP}
ENV USER_GRP=${USER_GRP}

WORKDIR ${ROOT_DIR}

# install dependencies
RUN apt update -y
RUN DEBIAN_FRONTEND=noninteractive apt install openssh-server git -y --no-install-recommends
RUN echo /usr/bin/git-shell >> /etc/shells

# copy user scripts to image
COPY scripts scripts

# copy scripts for docker, run setup
COPY --chmod=770 docker_scripts/* .
RUN ./setup.bash

ENTRYPOINT ["./main.bash"]
