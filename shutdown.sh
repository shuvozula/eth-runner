#!/bin/bash

#-----------------------
# For use with Crontab |
#-----------------------

my_dir="$(dirname $0)"

echo "Created wake-up alarm for 22:00hrs (10pm)....shutting down now..."
sudo sh -c "echo 0 > /sys/class/rtc/rtc0/wakealarm"  # clear the previous alarm
sudo sh $my_dir/switchoff_until.sh 22:00         # setup for wake-up at 10pm
