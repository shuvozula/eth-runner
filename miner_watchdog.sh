#!/bin/bash

# DISCLAIMER
# This is for Nvidia devices only, heavily relies on nvidia-smi to query device details.
# 
# Prerequisite: 
# - Requires nvidia-smi and nvidia tools library installed.


my_dir="$(dirname $0)"

# Minimum power consumed by Nvidia device (Watts), below which something suspicious is happening and miners need to be rebooted
powerLimit=55

# Maximum heat limit per Nvidia device allowed
heatLimit=78  # Farenheit

# Watchdog start-delay timer in seconds
startIn=120

# Minutes to sleep if either of the following (wattage, heat, etc.) send out alarms
wattage_sleep_timeout=5
heatage_sleep_timeout=20

#-------------------- DO NOT EDIT BELOW THIS LINE --------------------

# Stop/kill the miner processes and switch-off the machine for 5 minutes
stop_miners() {
  sh $my_dir/stop_miners.sh
  sleep 20;
        
  SLEEP_FOR=$1 # minutes
  SLEEP_FOR_SECS=$(($SLEEP_FOR*60))
  WAKEUP_IN=$(date +%H:%M -d "+$SLEEP_FOR_SECS seconds")
  echo "Going to sleep for $SLEEP_FOR minutes..., waking up at $WAKEUP_IN."
  sh $my_dir/switchoff_until.sh $WAKEUP_IN
  sleep 5
  exit 0
}

check_wattage() {
  watchPower="/usr/bin/nvidia-smi -q -d POWER | grep \"Power Draw\" | sed 's/[^0-9,.]*//g' | cut -d . -f 1"
  for device_wattage in $(eval ${watchPower}); do
    if [ "$device_wattage" -lt "$powerLimit" ]; then
      echo "`date`: Current power usage is $device_wattage < $powerLimit,so killing miners for 5 mins..."
      stop_miners $wattage_sleep_timeout
    fi
  done
}

check_heatage() {
  watchHeat="/usr/bin/nvidia-smi -q -d TEMPERATURE | grep \"GPU Current Temp\" | sed 's/[^0-9,.]*//g' | cut -d . -f 1"
  for device_heat in $(eval ${watchHeat}); do
    if [ "$device_heat" -gt "$heatLimit" ]; then
      echo "`date`: Current heat from GPUs is $device_heat > $heatLimit, so killing miners for 20 mins..."
      stop_miners $heatage_sleep_timeout
    fi
  done
}

start_watchdog() {
  echo "Watchdog: Starting in $startIn seconds..."
  sleep $startIn;
  echo "Watchdog started!"

  # repeatedly check for wattage consumption and heat production
  while :
  do
    check_wattage
    check_heatage
    sleep 10
  done
}

# start the watchdog
start_watchdog
