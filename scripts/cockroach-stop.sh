#!/bin/bash

set -o allexport
source /etc/cockroach/cockroach.conf
set +o allexport

/usr/bin/cockroach node drain --certs-dir=$COCKROACH_CERTS_DIR \
                              --host=$COCKROACH_HOST \
                              --drain-wait=$COCKROACH_DRAIN_WAIT \
                              --self

/usr/bin/kill -s SIGTERM `cat /var/run/cockroach/pid`
