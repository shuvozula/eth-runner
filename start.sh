#!/bin/bash

install_pipenv() {
	sudo apt install python python-pip
	pip install pipenv
}

my_dir="$(dirname $0)"
pipenv_home="/home/shuvo/.local/bin"

start_pause=30
echo "Sleeping for $start_pause seconds before starting mining...."

sleep $start_pause

for arg in "$@"; do
  case "$arg" in
    '--metrics')
        echo "Starting metrics services..."
        install_pipenv
        $pipenv_home/pipenv install
        $pipenv_home/pipenv run python $my_dir/metrics/start_metrics.py --props metrics/app.yml &

        echo "Starting FluentD collector..."
        docker stop fluent-logger
        docker build -t fluentd fluentd/.
        docker run -it -d --rm --name fluent-logger -v /var/log:/fluentd/log fluentd:latest
        ;;
  esac
done

if ! grep -q Screen7 /etc/X11/xorg.conf; then
  echo "Enabling Nvidia cards...."
  sudo sh $my_dir/nvidia/enable_nvidia.sh
  sleep 15
fi

echo "Tuning Nvidia cards...."
sudo sh $my_dir/nvidia/tune_nvidia.sh

# sleep for a bit to give time to the Nvidia drivers to calibrate
echo "Pausing...."
sleep 2

echo "Starting the Ethminers...."
sudo sh $my_dir/amd/run_amd.sh && sleep 30
sudo sh $my_dir/nvidia/run_nvidia.sh && sleep 120
