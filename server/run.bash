#!/bin/bash

cd "$(dirname "$0")"
source environment.bash

mkdir -p "$REPO_DIR" "$USER_DIR"
docker run \
    -v "$(realpath $REPO_DIR)":/root/repos \
    -v "$(realpath $USER_DIR)":/root/users \
    "$DOCKER_IMAGE_NAME"

