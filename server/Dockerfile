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
 && apt install openssh-server git sudo vim -y --no-install-recommends \
 && echo /usr/bin/git-shell >> /etc/shells

# Copy configs
COPY docker_configs/ssh_env.conf /etc/ssh/sshd_config.d
COPY docker_configs/sudo_user_manage /etc/sudoers.d

# Copy setup scripts and run them
RUN mkdir docker_scripts
COPY --chmod=770 docker_scripts/setup_sudoers.bash docker_scripts
RUN docker_scripts/setup_sudoers.bash

COPY --chmod=770 docker_scripts/setup_skel.bash docker_scripts
RUN docker_scripts/setup_skel.bash

COPY --chmod=770 docker_scripts/setup_owner.bash docker_scripts
RUN docker_scripts/setup_owner.bash

COPY --chmod=770 docker_scripts/setup_packages.bash docker_scripts
COPY scripts scripts
RUN docker_scripts/setup_packages.bash

COPY --chmod=770 docker_scripts/main.bash docker_scripts
ENTRYPOINT ["docker_scripts/main.bash"]
