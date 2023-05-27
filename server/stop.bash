#!/bin/bash -e

cd "$(dirname "$0")"
source env.bash

container_id="$( \
    sudo docker ps --format 'table {{.ID}}\t{{.Image}}' | \
    awk "{ if (\$2 == \"${DOCKER_IMAGE_NAME}\") { print \$1 } }"
)"
sudo docker kill -s TERM "$container_id"
