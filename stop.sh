#!/bin/bash

# Kill the watchdog
echo "Killing the watchdog...."
sudo kill -9 $(cat /var/log/miner_watchdog.pid)

# Kill the miners by their PIDs
echo "Killing all Ethminers....."
sudo kill -9 $(cat /var/log/ati_miner.pid)
sudo kill -9 $(cat /var/log/nvidia_miner.pid)

