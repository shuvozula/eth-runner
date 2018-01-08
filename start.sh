#!/bin/bash

my_dir="$(dirname $0)"

echo "Enabling Nvidia cards...."
sudo sh $my_dir/nvidia/enable_nvidia.sh

echo "Tuning Nvidia cards...."
sudo sh $my_dir/nvidia/tune_nvidia.sh

# sleep for 2 seconds to give time to the Nvidia drivers to calibrate
sleep 5

echo "Starting the Ethminers...."
sudo sh $my_dir/amd/run_amd.sh
sudo sh $my_dir/nvidia/run_nvidia.sh
