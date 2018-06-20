#!/bin/bash

# Kill the miners by their PIDs
echo "Killing all Ethminers....."
sudo kill -9 $(cat /var/log/ati_miner.pid)
sudo kill -9 $(cat /var/log/nvidia_miner.pid)

