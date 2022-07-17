#!/bin/bash

set -o allexport
source /etc/cockroach/cockroach.conf
set +o allexport

if [ "$(whoami)" == "cockroach" ]; then
	/usr/bin/cockroach cert create-client root
else
	sudo su - cockroach -c "/usr/bin/cockroach cert create-client root"
fi
