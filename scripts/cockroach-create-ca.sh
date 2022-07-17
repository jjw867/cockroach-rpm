#!/bin/bash

set -o allexport
source /etc/cockroach/cockroach.conf
set +o allexport

if [ "$(whoami)" == "cockroach" ]; then
	/usr/bin/cockroach cert create-ca
else
	sudo su - cockroach -c "/usr/bin/cockroach cert create-ca"
fi
