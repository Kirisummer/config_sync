#!/bin/bash -e

cd "${ROOT_DIR}/scripts"

make_pkg() {
    local pkg="$1"
    local group="$2"

    # copy __package helper to package name
    cp __package "$pkg"
    # give permissions to main script and its subscripts
    chmod -R 550 "$pkg" "_${pkg}"
    # make Owner and supplied group own the package
    chown -R "$OWNER_USER":"$group" "$pkg" "_$pkg"
}

# Helpers
chmod 550 __*
chown "$OWNER_USER":"$OWNER_GRP" __*

# Packages themselves
make_pkg self   "$USER_GRP"
make_pkg user   "$ADMIN_GRP"
make_pkg access "$ADMIN_GRP"
make_pkg repo   "$ADMIN_GRP"
make_pkg admin  "$OWNER_GRP"
