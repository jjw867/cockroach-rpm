#!/bin/sh

source /etc/cockroach/cockroach.conf

# get the default IP address of this node
IP_ADDR=$(ip route get 1 | awk '{print $(NF-2);exit}')

COCKROACH_MORE_NAMES=

if [ "$(whoami)" == "cockroach" ]; then
	/usr/bin/cockroach cert create-node $COCKROACH_ADVERTISE localhost $IP_ADDR $COCKROACH_MORE_NAMES 
else
	sudo su - cockroach -c "/usr/bin/cockroach cert create-node $COCKROACH_ADVERTISE localhost $IP_ADDR $COCKROACH_MORE_NAMES"
fi
