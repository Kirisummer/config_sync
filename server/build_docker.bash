#!/bin/bash

cd "$(dirname "$0")"
source environement.bash

export DOCKER_BUILDKIT=1
docker build -t config_server \
    --build-arg OWNER_GRP="$OWNER_GRP" \
    --build-arg ADMIN_GRP="$ADMIN_GRP" \
    --build-arg USER_GRP="$USER_GRP" \
    "$(dirname "$0")"
