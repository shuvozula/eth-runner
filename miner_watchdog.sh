#!/bin/bash

my_dir="$(dirname $0)"

powerLimit=55  # watts
watchPower="/usr/bin/nvidia-smi -q -d POWER | grep \"Power Draw\" | sed 's/[^0-9,.]*//g' | cut -d . -f 1"

heatLimit=78  # Farenheit
watchHeat="/usr/bin/nvidia-smi -q -d TEMPERATURE | grep \"GPU Current Temp\" | sed 's/[^0-9,.]*//g' | cut -d . -f 1"

startIn=120


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


echo "Watchdog: Starting in $startIn seconds..."
sleep $startIn;
echo "Watchdog started!"

while :
do
    for device_wattage in $(eval ${watchPower})
    do
        if [ "$device_wattage" -lt "$powerLimit" ]
        then
            echo "`date`: Current power usage is $device_wattage < $powerLimit,so killing miners for 5 mins..."
            
	    stop_miners 5
        fi
    done
    
    for device_heat in $(eval ${watchHeat})
    do
        if [ "$device_heat" -gt "$heatLimit" ]
        then
            echo "`date`: Current heat from GPUs is $device_heat > $heatLimit, so killing miners for 20 mins..."
       
            stop_miners 20
        fi
    done
    sleep 10
done

