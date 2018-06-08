#!/bin/bash
my_dir="$(dirname $0)"

limit=55
watchCmd="/usr/bin/nvidia-smi -q -d POWER | grep \"Power Draw\" | sed 's/[^0-9,.]*//g' | cut -d . -f 1"

startIn=120

echo "Watchdog: Starting in $startIn seconds..."
sleep $startIn;
echo "Watchdog started!"
while :
do
	for device_wattage in $watchCmd
	do
		# currentPowerUsage=$(eval ${watchCmd})
		# echo "Current power usage is $currentPowerUsage"
		# if [ "$currentPowerUsage" -lt "$limit" ]
		if [ "$device_wattage" -lt "$limit" ]
		then
			echo "`date`: Current power usage is $currentPowerUsage < $limit killing miner" | tee -a watchdogLog.log
		
			killall ethminer ; sleep 1; killall -9 ethminer
			sh $my_dir/stop.sh
			sleep 20;
		
			SLEEP_FOR=15
			echo "Going to sleep for $SLEEP_FOR minutes..."
			WAKEUP_IN_SECS=$((`date +%s` + $SLEEP_FOR*60))
			sh $my_dir/switchoff_until.sh $WAKEUP_IN_SECS
		fi
		sleep 10;
	done
done
