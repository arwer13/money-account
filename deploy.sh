#!/usr/bin/env bash
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <addr> <key_path>"
    exit 1
fi
set -ex
rsync -avz -e "ssh -i $2" --exclude ".git" --exclude ".idea" --exclude ".gitignore" --exclude "__pycache__" . "$1"
