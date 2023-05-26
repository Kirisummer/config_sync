#!/bin/bash -e
# Script to setup permissions

# Create groups
groupadd -- "$USER_GRP"
groupadd -- "$ADMIN_GRP"
groupadd -- "$OWNER_GRP"

# Create owner account with default password, add owner to all groups, setup home dir
useradd \
    --base-dir "$USER_DIR" \
    --create-home \
    --groups "$USER_GRP","$ADMIN_GRP","$OWNER_GRP" \
    --no-user-group \
    --shell /usr/bin/git-shell \
    "$OWNER_USER"
chpasswd <<< "$OWNER_USER:$OWNER_USER"

# Make owner and their group own root directory
chown "$OWNER_USER":"$OWNER_GRP" "$ROOT_DIR"

# Setup script packages
cd "$CMD_DIR"

make_pkg() {
    local pkg="$1"
    local group="$2"

    # copy __package helper to package name
    cp __package "$pkg"
    # give permissions to main script and its subscripts
    chmod -R 750 "$pkg" "_${pkg}"
    # make Owner and supplied group own the package
    chown -R "$OWNER_USER":"$group" "$pkg" "_$pkg"
}

# Helpers
chmod 750 __*
chown "$OWNER_USER":"$OWNER_GRP" __*

# Packages themselves
make_pkg self   "$USER_GRP"
make_pkg user   "$ADMIN_GRP"
make_pkg access "$ADMIN_GRP"
make_pkg repo   "$ADMIN_GRP"
make_pkg admin  "$OWNER_GRP"
