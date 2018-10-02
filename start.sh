#!/bin/bash

my_dir="$(dirname $0)"

start_pause=60
echo "Sleeping for $start_pause seconds before starting mining...."

sleep $start_pause

echo "Enabling Nvidia cards...."
sudo sh $my_dir/nvidia/enable_nvidia.sh

sleep 15

echo "Tuning Nvidia cards...."
sudo sh $my_dir/nvidia/tune_nvidia.sh

# sleep for a bit to give time to the Nvidia drivers to calibrate
echo "Pausing...."
sleep 2

echo "Starting the Ethminers...."
sudo sh $my_dir/amd/run_amd.sh
sleep 30
sudo sh $my_dir/nvidia/run_nvidia.sh
sleep 10

# start watchdog
echo "Starting watchdog...."
sudo sh $my_dir/miner_watchdog.sh &
sleep 10

watchdogpid=$(ps -eaf | grep "[m]iner_watchdog" | awk {'print$2'})
echo $watchdogpid > /var/log/miner_watchdog.pid

for arg in "$@"; do
  case "$arg" in
    '--start-clean') 
        echo "Cleaning up old containers..."
        docker stop $(docker ps -aq) && docker rm $(docker ps -aq)
        ;;

    '--metrics') 
        echo "Starting metrics services"
        if [ -z $(which docker) ]; then
          echo "ERROR: No Docker installed! Can't start Metrics server..."
          exit 1
        fi
        echo 'Starting Nvidia metrics collection....'
        sudo python $my_dir/metrics/collect_nvidia_metrics.py &
        sleep 10
        echo 'Starting AMD + CPU metrics collection....'
        sudo python $my_dir/metrics/collect_amd_cpu_metrics.py &
        ;;
  esac
done
