#!/bin/bash

METRICS_SERVER_NAME=eth-metrics-influx
METRICS_DB=ethmetrics

if [[ $(docker ps -a | grep $METRICS_SERVER_NAME) ]]; then
  docker start $METRICS_SERVER_NAME
else
  echo "Creating container...."
  docker run \
    --ulimit nofile=66000:66000 \
    -d \
    --name $METRICS_SERVER_NAME \
    -p 3003:3003 \
    -p 3004:8888 \
    -p 8086:8086 \
    -p 22022:22 \
    -p 8125:8125/udp \
    samuelebistoletti/docker-statsd-influxdb-grafana:latest

  echo "Sleeping for 10 secs for InfluxDB to startup..."
  sleep 10

  echo "Creating DB: $METRICS_DB"
  curl -i -XPOST http://localhost:8086/query --data-urlencode "q=CREATE DATABASE ${METRICS_DB}"
fi

upload_wattage_metrics() {
  watchPower="/usr/bin/nvidia-smi -q -d POWER | grep \"Power Draw\" | sed 's/[^0-9,.]*//g' | cut -d . -f 1"
  i=0
  host="http://localhost:8086/write?db=${METRICS_DB}"
  for device_wattage in $(eval ${watchPower}); do
    data_binary="gpu${i}heat,host=minar,gpu=${i} power=${device_wattage}"
    echo $data_binary | curl -i -XPOST $host --data-binary @-
    ((i++))
  done
}

upload_heat_metrics() {
  watchHeat="/usr/bin/nvidia-smi -q -d TEMPERATURE | grep \"GPU Current Temp\" | sed 's/[^0-9,.]*//g' | cut -d . -f 1"
  i=0
  host="http://localhost:8086/write?db=${METRICS_DB}"
  for device_heatage in $(eval ${watchHeat}); do
    data_binary="gpu${i}heat,host=minar,gpu=${i} heat=${device_heatage}"
    echo $data_binary | curl -i -XPOST $host --data-binary @-
    ((i++))
  done
}

start_collecting_metrics() {
  echo "Starting data collection..."
  while :
  do
    upload_wattage_metrics
    upload_heat_metrics
    sleep 1
  done
}
	
start_collecting_metrics
	
