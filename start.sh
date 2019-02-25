#!/bin/bash

my_dir="$(dirname $0)"

start_pause=0
echo "Sleeping for $start_pause seconds before starting mining...."

sleep $start_pause

if ! grep -q Screen7 /etc/X11/xorg.conf; then
  echo "Enabling Nvidia cards...."
  sudo sh $my_dir/nvidia/enable_nvidia.sh
  sleep 15
fi

echo "Tuning Nvidia cards...."
sudo sh $my_dir/nvidia/tune_nvidia.sh

# sleep for a bit to give time to the Nvidia drivers to calibrate
echo "Pausing...."
sleep 2

echo "Starting the Ethminers...."
sudo sh $my_dir/amd/run_amd.sh && sleep 30
sudo sh $my_dir/nvidia/run_nvidia.sh && sleep 120

for arg in "$@"; do
  case "$arg" in
    '--metrics')
        echo "Starting metrics services"
        pipenv install
        pipenv run python $my_dir/metrics/start_metrics.py --props metrics/app.yml &
        ;;
  esac
done
