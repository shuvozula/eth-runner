#!/bin/bash

# Watchdog start-delay timer in seconds
START_IN=10
PAUSE=5  # seconds
METRICS_DB=ethmetrics
HOST="http://localhost:8086/write?db=${METRICS_DB}"
GPUS=$(sudo DISPLAY=:0 XAUTHORITY=/var/run/lightdm/root/:0 nvidia-settings -c :0 -q gpus)

upload_wattage_metrics() {
  watchPower="/usr/bin/nvidia-smi -q -d POWER | grep \"Power Draw\" | sed 's/[^0-9,.]*//g' | cut -d . -f 1"
  i=0
  for device_wattage in $(eval ${watchPower}); do
    data_binary="gpu${i}power,host=minar,gpu=${i} power=${device_wattage} $1"
    echo $data_binary | curl -s -i -XPOST $HOST --data-binary @- 2>&1 >/dev/null
    i=$((i + 1))
  done
}

upload_heat_metrics() {
  watchHeat="/usr/bin/nvidia-smi -q -d TEMPERATURE | grep \"GPU Current Temp\" | sed 's/[^0-9,.]*//g' | cut -d . -f 1"
  i=0
  for device_heatage in $(eval ${watchHeat}); do
    data_binary="gpu${i}heat,host=minar,gpu=${i} heat=${device_heatage} $1"
    echo $data_binary | curl -s -i -XPOST $HOST --data-binary @- 2>&1 >/dev/null
    i=$((i + 1))
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
  echo "Data-Collector: Starting in $START_IN seconds..."
  sleep $START_IN;
  echo "Starting data collection..."
  while :
  do
    nanoseconds=$(date +%s%N)  # nanoseconds since epoch
    upload_wattage_metrics $nanoseconds
    upload_heat_metrics $nanoseconds
    upload_fan_metrics $nanoseconds
    sleep $PAUSE
  done
}

# record the PID
sudo echo $$ > /var/log/nvidia_metrics_collector.pid

# start the madness
start_collecting_metrics
