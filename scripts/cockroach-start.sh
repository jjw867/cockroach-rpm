#!/bin/bash

set -o allexport
source /etc/cockroach/cockroach.conf
set +o allexport

TimeSync=$(timedatectl | awk '/System clock synchronized/{print $NF}')
if [ $TimeSync == "no" ]; then
        echo "Time is not synchronized, aborting startup"
        exit 6
fi

NTPService=$(timedatectl | awk '/NTP service/{print $NF}')
if [ $NTPService == "inactive" ]; then
        echo "NTP inactive, aborting startup"
        exit 6
fi

if [ $COCKROACH_START == "start-single-node" ]; then
    /usr/bin/cockroach $COCKROACH_START --certs-dir=$COCKROACH_CERTS_DIR \
                                        --store=$COCKROACH_STORAGE1 \
                                        --cache=$COCKROACH_CACHE \
                                        --max-sql-memory=$COCKROACH_SQL_MEMORY \
                                        --log-config-file=$COCKROACH_LOG_CONFIG \
                                        --advertise-addr=$COCKROACH_ADVERTISE \
                                        --http-addr=$COCKROACH_UI_PORT \
					--pid-file=/var/run/cockroach/pid \
                                        --background
else
    /usr/bin/cockroach $COCKROACH_START --certs-dir=$COCKROACH_CERTS_DIR \
                                        --store=$COCKROACH_STORAGE1 \
                                        --cache=$COCKROACH_CACHE \
                                        --max-sql-memory=$COCKROACH_SQL_MEMORY \
                                        --log-config-file=$COCKROACH_LOG_CONFIG \
                                        --advertise-addr=$COCKROACH_ADVERTISE \
					--listen-addr=$COCKROACH_ADVERTISE \
                                        --http-addr=$COCKROACH_UI_PORT \
					--pid-file=/var/run/cockroach/pid \
					--join=$COCKROACH_JOIN_HOSTS \
                                        --locality=$COCKROACH_LOCALITY \
                                        --background
fi
