#!/bin/bash

my_dir="$(dirname $0)"

# Kill the miners by their PIDs
echo "Killing all Ethminers....."
sudo kill -9 $(cat /var/log/ati_miner.pid)
sudo kill -9 $(cat /var/log/nvidia_miner.pid)

if [[ $1 == --metrics ]]; then
  echo 'Killing metrics data collection...'
  sudo sh $my_dir/metrics/stop_metrics.sh
fi
