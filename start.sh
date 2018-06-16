#!/bin/bash

my_dir="$(dirname $0)"

start_pause=30
echo "Sleeping for $start_pause seconds before starting mining...."

echo "Enabling Nvidia cards...."
sudo sh $my_dir/nvidia/enable_nvidia.sh

sleep 2

echo "Tuning Nvidia cards...."
sudo sh $my_dir/nvidia/tune_nvidia.sh

# sleep for a bit to give time to the Nvidia drivers to calibrate
echo "Pausing...."
sleep 2

echo "Starting the Ethminers...."
sudo sh $my_dir/amd/run_amd.sh
sleep 30
sudo sh $my_dir/nvidia/run_nvidia.sh

# start watchdog
echo "Starting watchdog...."
sh $my_dir/miner_watchdog.sh & echo $! /var/log/miner_watchdog.pid
