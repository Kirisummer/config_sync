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

# Run ssh service
service ssh start

(while :; do true; done) &
wait "${!}"
