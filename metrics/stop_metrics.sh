#!/bin/bash

METRICS_SERVER_NAME=eth-metrics-influx

# stop the metrics collection script
echo "Stopping metrics collectors..."
sudo kill -9 $(cat /var/log/nvidia_metrics_collector.pid)
sudo kill -9 $(cat /var/log/amd_cpu_metrics_collectors.pid)

# stop the metrics containers
if [ "$(docker ps -a | grep $METRICS_SERVER_NAME)" ]; then
  echo "Stopping metrics server..."
  docker stop $METRICS_SERVER_NAME
fi
