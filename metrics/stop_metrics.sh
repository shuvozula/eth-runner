#!/bin/bash

METRICS_SERVER_NAME=eth-metrics-influx

# stop the metrics collection script
echo "Stopping metrics collectors..."
sudo kill $(cat /var/log/metrics_collector.pid)

