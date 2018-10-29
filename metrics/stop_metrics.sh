#!/bin/bash

METRICS_SERVER_NAME=eth-metrics-influx

# stop the metrics collection script
echo "Stopping metrics collectors..."
sudo kill $(cat /var/log/nvidia_metrics_collector.pid)
sudo kill $(cat /var/log/amd_cpu_metrics_collector.pid)

