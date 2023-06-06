#!/bin/bash -e

cd "$(dirname "$0")"
source env.bash

mkdir -p "$REPO_DIR" "$USER_DIR" "$PASSWD_DIR"
sudo docker run -d --rm \
    -v "$(realpath $REPO_DIR)":"$ROOT_DIR"/repos \
    -v "$(realpath $USER_DIR)":"$ROOT_DIR"/users \
    -v "$(realpath $PASSWD_DIR)":"$ROOT_DIR"/passwd \
    -p 8022:22 \
    "$DOCKER_IMAGE_NAME" 

