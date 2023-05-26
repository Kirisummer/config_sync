#!/bin/bash -e
# Script that acts as entrypoint and catches shutdown signal

function backup_passwd() {
    echo Trap activated
    ls /etc/{passwd,shadow,group,gshadow,sub{gid,uid}}
    cp /etc/{passwd,shadow,group,gshadow,sub{gid,uid}} "${ROOT_DIR}/passwd"
    exit
}

trap backup_passwd SIGINT SIGTERM
trap -p

# Restore users and groups
cp "${ROOT_DIR}/passwd/"* /etc || true

# Create owner directory if it's missing
# It cannot be created at startup because we cannot mount users on build
# and overwrite users dir when it is mounted on run
owner_dir="${ROOT_DIR}/users/${OWNER_USER}"
if ! [ -d "$owner_dir" ]; then
    cp -r "${ROOT_DIR}/dir_skel" "$owner_dir"
    rmdir "${owner_dir}/repos"
    ln -s "${ROOT_DIR}/repos" "${owner_dir}/repos"
    chown "${OWNER_USER}:${OWNER_GRP}" "$owner_dir"
fi

# Run ssh service
service ssh start

(while :; do true; done) &
wait "${!}"
