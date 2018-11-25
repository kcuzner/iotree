#!/usr/bin/bash

source run.settings.sh

trap 'kill $SSH_PID; exit' SIGINT
ssh -i $SSHTUNNEL_KEY -T -N -L 6379:127.0.0.1:6379 ${SSHTUNNEL_USER}@${SSHTUNNEL_HOST} &
SSH_PID=$!

while true; do
    nc -z localhost 6379 && break;
    if ! kill -0 $SSH_PID; then
        exit 1
    fi
    sleep 0.1
done

python2 christmastree.py

kill $SSH_PID

