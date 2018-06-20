#!/bin/bash

# Kill the watchdog
echo "Killing the watchdog...."
sudo kill -9 $(cat /var/log/miner_watchdog.pid)

