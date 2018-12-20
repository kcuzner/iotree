#!/usr/bin/bash

source run.settings.sh

run(){
    { echo "Starting $1"; } 2> /dev/null
    python2 $1
    { echo "Python $1: Status $?"; } 2> /dev/null
}

run webcam.py &
run ws2811.py &

for job in `jobs -p`
do
    wait $job
done

