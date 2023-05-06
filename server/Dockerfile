FROM ubuntu:20.04

ENV CMD_DIR=/root/scripts
ENV REPO_DIR=/root/repos
ENV USER_DIR=/root/users

ENV OWNER_GRP=owner
ENV ADMIN_GRP=admin
ENV USER_GRP=user

WORKDIR /root
COPY prepare_env.bash .
RUN chmod +x prepare_env.bash
RUN ./prepare_env.bash

COPY scripts /root/scripts
COPY deploy_scripts.bash .
RUN chmod +x deploy_scripts.bash
RUN ./deploy_scripts.bash
