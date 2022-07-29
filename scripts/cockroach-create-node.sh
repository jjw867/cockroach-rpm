#!/bin/bash

set -o allexport
source /etc/cockroach/cockroach.conf
set +o allexport

# get the default IP address of this node
IP_ADDR=$(ip route get 1 | awk '{print $(NF-2);exit}')

# get the FQDN
FQDN=$(host -TtA $(hostname -s) | grep "has address" | awk '{print $1}')

if [ "$(whoami)" == "cockroach" ]; then
	/usr/bin/cockroach cert create-node $COCKROACH_ADVERTISE localhost $IP_ADDR $COCKROACH_MORE_NAMES $FQDN 127.0.0.1
else
	sudo su - cockroach -c "/usr/bin/cockroach cert create-node $COCKROACH_ADVERTISE localhost $IP_ADDR $COCKROACH_MORE_NAMES $FQDN 127.0.0.1"
fi
