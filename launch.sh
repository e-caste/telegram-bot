#!/bin/bash

docker run \
    --restart unless-stopped \
    -v "$PWD"/data:/bot/data \
    -v "$PWD"/logs:/bot/logs \
    -v "$PWD"/pics:/bot/pics:ro \
    -e TOKEN="TODO" \
    -e CST_CID="TODO" \
    -itd pibot:latest
