#!/usr/bin/env bash

echo "Enabling Nvidia cards...."
sudo sh nvidia/enable_nvidia.sh

echo "Tuning Nvidia cards...."
sudo sh nvidia/tune_nvidia.sh

# sleep for 2 seconds to give time to the Nvidia drivers to calibrate
sleep 5

echo "Starting the Ethminers...."
sudo sh amd/run_amd.sh && sudo sh nvidia/run_nvidia.sh
