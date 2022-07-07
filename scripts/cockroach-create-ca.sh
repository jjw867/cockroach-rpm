#!/bin/sh

source /etc/cockroach/cockroach.conf

if [ "$(whoami)" == "cockroach" ]; then
	/usr/bin/cockroach cert create-ca
else
	sudo su - cockroach -c "/usr/bin/cockroach cert create-ca"
fi
