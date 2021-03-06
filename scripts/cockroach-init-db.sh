#!/bin/bash

set -o allexport
source /etc/cockroach/cockroach.conf
set +o allexport

if [ $COCKROACH_START == "start-single-node" ]; then
	echo "Init not needed for $COCKROACH_START setting"
	exit 0
fi

if [ "$(whoami)" == "cockroach" ]; then
	/usr/bin/cockroach init --host=$COCKROACH_ADVERTISE
else
	sudo su - cockroach -c "/usr/bin/cockroach init"
fi
