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
