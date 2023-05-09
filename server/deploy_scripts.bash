#!/bin/bash -e

cd "$CMD_DIR"

owner=$(grep -E "\<"$OWNER_GRP"\>" /etc/group | cut -d: -f4 | cut -d, -f1)

make_pkg() {
    local pkg="$1"
    local group="$2"

    cp __package "$pkg"
    chmod 750 "$pkg"
    chmod 750 _"$pkg"
    chown "$owner":"$group" "$pkg"
}

# Setup helper permissions
chmod 750 __*
chown "$owner":"$group" __*

# Setup packages
make_pkg self   "$USER_GRP"
make_pkg user   "$ADMIN_GRP"
make_pkg access "$ADMIN_GRP"
make_pkg repo   "$ADMIN_GRP"
make_pkg admin  "$OWNER_GRP"
