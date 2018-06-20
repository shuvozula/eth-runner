#!/bin/bash

my_dir="$(dirname $0)"

sh $my_dir/stop_watchdog.sh
sh $my_dir/stop_miners.sh
