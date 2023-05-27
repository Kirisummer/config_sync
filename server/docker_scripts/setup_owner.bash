#!/bin/bash -e

groupadd -- "$USER_GRP"
groupadd -- "$ADMIN_GRP"
groupadd -- "$OWNER_GRP"
groupadd sudoers
useradd \
    --create-home \
    --base-dir "${ROOT_DIR}/users" \
    --no-user-group \
    --groups "${USER_GRP},${ADMIN_GRP},${OWNER_GRP},sudoers" \
    --shell /usr/bin/git-shell \
    "$OWNER_USER"
chpasswd <<< "${OWNER_USER}:${OWNER_USER}"
chown -R "${OWNER_USER}:${OWNER_GRP}" "$ROOT_DIR"
chmod -R 775 "$ROOT_DIR"
