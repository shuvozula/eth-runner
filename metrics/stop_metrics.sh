#!/bin/bash

METRICS_SERVER_NAME=eth-metrics-influx


if [[ $(docker ps -a | grep $METRICS_SERVER_NAME) ]]; then
	docker stop $METRICS_SERVER_NAME
fi
