#!/bin/bash -e
# Script that acts as entrypoint and catches shutdown signal

function backup_passwd() {
    echo Trap activated
    ls /etc/{passwd,shadow,group,gshadow,sub{gid,uid}}
    cp /etc/{passwd,shadow,group,gshadow,sub{gid,uid}} "$PASSWD_DIR"
    exit
}

trap backup_passwd SIGINT SIGTERM
trap -p

# Restore users and groups
cp "$PASSWD_DIR"/* /etc || true

# Create owner directory if it's missing
# It cannot be created at startup because we cannot mount users on build
# and overwrite users dir when it is mounted on run
owner_dir="$USER_DIR"/"$OWNER_USER"
if ! [ -d "$owner_dir" ]; then
    mkdir "$USER_DIR"/"$OWNER_USER"
    chown "$OWNER_USER":"$OWNER_GRP" "$USER_DIR"/"$OWNER_USER"
    ln -s "$CMD_DIR" "$USER_DIR"/"$OWNER_USER"/git-shell-commands
    ln -s "$REPO_DIR" "$USER_DIR"/"$OWNER_USER"/repos
fi

# Run ssh service
service ssh start

(while :; do true; done) &
wait "${!}"
