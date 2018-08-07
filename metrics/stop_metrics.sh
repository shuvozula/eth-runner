#!/bin/bash

METRICS_SERVER_NAME=eth-metrics-influx

# stop the metrics collection script
sudo kill -9 $(cat /var/log/metrics_collection.pid)

# stop the metrics containers
if [[ $(docker ps -a | grep $METRICS_SERVER_NAME) ]]; then
	echo "Stopping metrics server..."
	docker stop $METRICS_SERVER_NAME
fi
