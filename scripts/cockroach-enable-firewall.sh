#!/bin/bash

set -o allexport
source /etc/cockroach/cockroach.conf
set +o allexport

echo "Enabling CockroachDB on port 26257"
firewall-cmd --add-service=cockroach-server --permanent

if [ "$COCKROACH_PORT" != "26257" ]; then
	echo "Cockroach not configured for port 26257, update firewall configuration"
fi

if [ ! "$COCKROACH_UI_PORT" ]; then
	firewall-cmd --add-service=cockroach-ui --permanent
	echo "Enabling CockroachDB Web UI on port 8080"
fi

firewall-cmd --reload

