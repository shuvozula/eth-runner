#!/bin/bash

METRICS_DB=ethmetrics
HOST="http://localhost:8086/write?db=${METRICS_DB}"

upload_wattage_metrics() {
  watchPower="/usr/bin/nvidia-smi -q -d POWER | grep \"Power Draw\" | sed 's/[^0-9,.]*//g' | cut -d . -f 1"
  i=0
  for device_wattage in $(eval ${watchPower}); do
    data_binary="gpu${i}power,host=minar,gpu=${i} power=${device_wattage} $@"
    echo $data_binary | curl -s -i -XPOST $HOST --data-binary @- 2>&1 >/dev/null
    ((i++))
  done
}

upload_heat_metrics() {
  watchHeat="/usr/bin/nvidia-smi -q -d TEMPERATURE | grep \"GPU Current Temp\" | sed 's/[^0-9,.]*//g' | cut -d . -f 1"
  i=0
  for device_heatage in $(eval ${watchHeat}); do
    data_binary="gpu${i}heat,host=minar,gpu=${i} heat=${device_heatage} $@"
    echo $data_binary | curl -s -i -XPOST $HOST --data-binary @- 2>&1 >/dev/null
    ((i++))
  done
}

start_collecting_metrics() {
  echo "Starting data collection..."
  while :
  do
    date=$(date +%s)
    upload_wattage_metrics $date
    upload_heat_metrics $date
    sleep 1
  done
}

echo $$ > /var/log/metrics_collection.pid
start_collecting_metrics
