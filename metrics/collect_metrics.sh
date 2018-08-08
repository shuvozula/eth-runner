#!/bin/bash

METRICS_DB=ethmetrics
HOST="http://localhost:8086/write?db=${METRICS_DB}"
GPUS=$(sudo DISPLAY=:0 XAUTHORITY=/var/run/lightdm/root/:0 nvidia-settings -c :0 -q gpus)

upload_wattage_metrics() {
  watchPower="/usr/bin/nvidia-smi -q -d POWER | grep \"Power Draw\" | sed 's/[^0-9,.]*//g' | cut -d . -f 1"
  i=0
  for device_wattage in $(eval ${watchPower}); do
    data_binary="gpu${i}power,host=minar,gpu=${i} power=${device_wattage} $1"
    echo $data_binary | curl -s -i -XPOST $HOST --data-binary @- 2>&1 >/dev/null
    ((i++))
  done
}

upload_heat_metrics() {
  watchHeat="/usr/bin/nvidia-smi -q -d TEMPERATURE | grep \"GPU Current Temp\" | sed 's/[^0-9,.]*//g' | cut -d . -f 1"
  i=0
  for device_heatage in $(eval ${watchHeat}); do
    data_binary="gpu${i}heat,host=minar,gpu=${i} heat=${device_heatage} $1"
    echo $data_binary | curl -s -i -XPOST $HOST --data-binary @- 2>&1 >/dev/null
    ((i++))
  done
}

upload_fan_metrics() {
  for gpu_index in $(echo $GPUS | grep -o "\[[0-9]*\]" | grep -o "[0-9]*"); do
    watchFanCmd="/usr/bin/nvidia-smi -i ${gpu_index} -q | grep \"Fan Speed\" | sed 's/[^0-9,.]*//g' | cut -d . -f 1"
    fanData=$(eval ${watchFanCmd})
    data_binary="gpu${gpu_index}fanspeed,host=minar,gpu=${gpu_index} fanspeed=${fanData} $1"
    echo $data_binary | curl -s -i -XPOST $HOST --data-binary @- 2>&1 >/dev/null
  done
}

start_collecting_metrics() {
  echo "Starting data collection..."
  while :
  do
    date=$(date +%s%N)  # nanoseconds since epoch
    upload_wattage_metrics $date
    upload_heat_metrics $date
    upload_fan_metrics $date
    sleep 1
  done
}

# record the PID
sudo echo $$ > /var/log/metrics_collection.pid

# start the madness
start_collecting_metrics
