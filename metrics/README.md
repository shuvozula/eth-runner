# Metrics Server for Eth-Runner

## Prerequisites
* Docker

## Start metrics server and data collection
The `start_metrics.sh` script gets executed if the `--metrics` argument is passed to the start script, like so: `../start.sh --metrics`. Otherwise, it can be executed independently or on another box, however your layout is.

The `start_metrics.sh` script does the following:
- starts the InfluxDB + Grafana + Telegraf(StatsD) docker container
- collects the Nvidia GPU Watts and Heat readings and `curl`s the data to InfluxDB.

## Setup Grafana
Login to Grafana using the following credentials:
```
username: root
password: root
```
The InfluxDB datasource is not initially setup, so navigate to create a new datasource, select InfluxDB as the type and then use the database name `ethmetrics`, no login required. The data will then be uploaded by `start_metrics.sh` once it starts running.

### Creating dashboards
The dashboard is initially not setup as well, so that's a manual effort of creating one's own custom dashboards, or.... use the `sample_grafana_metrics_dashboard.json` provided and import into Grafana to use it as a starting point for your own dashboards.
