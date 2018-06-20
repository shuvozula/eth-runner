#!/bin/bash
my_dir="$(dirname $0)"

limit=55  # watts
watchCmd="/usr/bin/nvidia-smi -q -d POWER | grep \"Power Draw\" | sed 's/[^0-9,.]*//g' | cut -d . -f 1"

startIn=120

echo "Watchdog: Starting in $startIn seconds..."
sleep $startIn;
echo "Watchdog started!"
while :
do
    for device_wattage in $(eval ${watchCmd})
    do
        if [ "$device_wattage" -lt "$limit" ]
        then
            echo "`date`: Current power usage is $currentPowerUsage < $limit killing miner"
        
            sh $my_dir/stop_miners.sh
            sleep 20;
        
            SLEEP_FOR=5 # minutes
            SLEEP_FOR_SECS=$(($SLEEP_FOR*60))
            WAKEUP_IN=$(date +%H:%M -d "+$SLEEP_FOR_SECS seconds")
            echo "Going to sleep for $SLEEP_FOR minutes..., waking up at $WAKEUP_IN."
            sh $my_dir/switchoff_until.sh $WAKEUP_IN
            sleep 5
            exit 0
        fi
        sleep 10;
    done
done
