#!/bin/sh

source /etc/cockroach/cockroach.conf

if [ "$(whoami)" == "cockroach" ]; then
	/usr/bin/cockroach cert create-client root
else
	sudo su - cockroach -c "/usr/bin/cockroach cert create-client root"
fi
