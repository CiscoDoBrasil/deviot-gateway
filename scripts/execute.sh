#!/bin/bash
#
# Initialization script for DevIoT Gateway Service
#

INSTALL_DIR=/opt/deviot-gateway
PID_FILE=/tmp/deviot-gateway.pid

cd $INSTALL_DIR

wait_for_network() {
    echo -n "Waitig for network connectivity"
    while ! ip address show | grep -v "169\.254\." | grep "inet " > /dev/null
    do
        echo -n "."
        sleep 5
    done
    echo " ok!"
}

start() {
    if [ ! -e $PID_FILE ]
    then
        wait_for_network
        python app.py &
        echo $! > $PID_FILE
    else
        echo "DevIoT Service is already running. If not, remove $PID_FILE."
        exit -1
    fi
}

stop() {
    if [ -e $PID_FILE ]
    then
        cat $PID_FILE | xargs kill -9
        rm -f $PID_FILE
    else
        echo "DevIoT Gateway Service is not running."
        exit -1
    fi
}

case $1 in
    start|stop) "$1";;
    *) echo "Please use 'start' or 'stop' to control DevIoT Service Gateway."
esac

exit 0

