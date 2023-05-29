#!/bin/bash

cd "$(dirname "$0")"
source env.bash

sudo docker buildx build "$@" -t "$DOCKER_IMAGE_NAME" \
    --build-arg ROOT_DIR="$ROOT_DIR" \
    --build-arg OWNER_USER="$OWNER_GRP" \
    --build-arg OWNER_GRP="$OWNER_GRP" \
    --build-arg ADMIN_GRP="$ADMIN_GRP" \
    --build-arg USER_GRP="$USER_GRP" \
    .
