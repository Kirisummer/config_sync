FROM ubuntu:20.04

# Setup env 
ARG OWNER_USER
ARG OWNER_GRP
ARG ADMIN_GRP
ARG USER_GRP

ENV ROOT_DIR=/config-server
ENV OWNER_USER=${OWNER_USER}
ENV OWNER_GRP=${OWNER_GRP}
ENV ADMIN_GRP=${ADMIN_GRP}
ENV USER_GRP=${USER_GRP}

WORKDIR ${ROOT_DIR}

# Install dependencies
RUN DEBIAN_FRONTEND=noninteractive apt update -y \
 && apt install openssh-server git vim -y --no-install-recommends \
 && echo /usr/bin/git-shell >> /etc/shells

# Copy docker scripts, configs and server scripts
COPY --chmod=770 docker_scripts docker_scripts
COPY scripts scripts
COPY docker_configs/ssh_env.conf /etc/ssh/sshd_config.d

# Run setup scripts
RUN docker_scripts/setup_skel.bash
RUN docker_scripts/setup_owner.bash
RUN docker_scripts/setup_packages.bash

ENTRYPOINT ["./main.bash"]
