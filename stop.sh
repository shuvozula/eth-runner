#!/bin/bash

my_dir="$(dirname $0)"

sh $my_dir/stop_watchdog.sh
sh $my_dir/stop_miners.sh

if [ "$1" -eq '--metrics' ]; then
  echo 'Killing metrics containers and data collection...'
  sh $my_dir/metrics/stop_metrics.sh
fi
