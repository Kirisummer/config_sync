#!/bin/bash -e

mkdir -p "${ROOT_DIR}/dir_skel/_repos" "${ROOT_DIR}/dir_skel/.ssh"
chmod 700 "${ROOT_DIR}/dir_skel/.ssh"
ln -s "${ROOT_DIR}/scripts" "${ROOT_DIR}/dir_skel/git-shell-commands"

vars=(ROOT_DIR OWNER_USER OWNER_GRP ADMIN_GRP USER_GRP)
for var in "${vars[@]}"; do
    printf '%s=%s\n' "$var" "${!var}" >> "${ROOT_DIR}/dir_skel/.ssh/environment"
done

cd "${ROOT_DIR}/dir_skel"
ln -s _repos repos
