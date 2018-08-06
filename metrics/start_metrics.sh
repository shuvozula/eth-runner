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

  echo "Creating DB: $METRICS_DB"
  curl -i -XPOST http://localhost:8086/query --data-urlencode "q=CREATE DATABASE $METRICS_DB"
fi

echo "Sleeping for 10 secs for InfluxDB to startup..."
sleep 10

upload_wattage_metrics() {
  watchPower="/usr/bin/nvidia-smi -q -d POWER | grep \"Power Draw\" | sed 's/[^0-9,.]*//g' | cut -d . -f 1"
  currTime=$(date +%s)
  i=0
  for device_wattage in $(eval ${watchPower}); do
    curl -i -XPOST 'http://localhost:8086/write?db=${METRICS_DB}' \
        --data-binary 'gpu_${i}_power,host=minar value=${device_wattage} ${currTime}'
    ((i++))
  done
}

start_collecting_metrics() {
  echo "Starting data collection..."
  while :
  do
    upload_wattage_metrics
    sleep 1
  done
}
	
start_collecting_metrics
	
