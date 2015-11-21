#!/bin/bash

control_c() {
    kill $PID
    exit
}

trap control_c SIGINT

if [ "$#" -ne 1 ]; then
    echo "No file to run specified"
    exit 1
fi

while true; do
    $@ &
    PID=$!
    echo $PID
    sleep 1
    inotifywait $1
    kill $PID
done
