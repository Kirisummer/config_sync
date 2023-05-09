FROM ubuntu:20.04

ARG OWNER_GRP
ARG ADMIN_GRP
ARG USER_GRP

ENV CMD_DIR=/root/scripts
ENV REPO_DIR=/root/repos
ENV USER_DIR=/root/users

ENV OWNER_GRP=${OWNER_GRP}
ENV ADMIN_GRP=${ADMIN_GRP}
ENV USER_GRP=${USER_GRP}

COPY scripts /root/scripts
COPY deploy_scripts.bash .
RUN ./deploy_scripts.bash
