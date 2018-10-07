#!/bin/bash

my_dir="$(dirname $0)"

# start the metrics collection scripts
echo "Starting AMD GPU +CPU metrics collectors..."
sudo python $my_dir/collect_amd_cpu_metrics.py >> $my_dir/../logs/metrics_runner.log &

echo "Starting NVIDI GPU metrics collectors..."
sudo python $my_dir/collect_nvidia_metrics.py >> $my_dir/../logs/metrics_nvidia.log &
