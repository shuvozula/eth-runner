#!/bin/bash

# Auto switchoff and wake-up script
#
# Puts the computer on standby and automatically wakes it up at specified time
#
# Written by Romke van der Meulen <redge.online@gmail.com>
# Minor mods fossfreedom for AskUbuntu
#
# Takes a 24hour time HH:MM as its argument
# Example:
# switchoff_until 9:30
# switchoff_until 18:45

# ------------------------------------------------------
# Argument check
if [ $# -lt 1 ]; then
    echo "Usage: switchoff_until HH:MM"
    exit
fi

# Check whether specified time today or tomorrow
DESIRED=$((`date +%s -d "$1"`))
NOW=$((`date +%s`))
if [ $DESIRED -lt $NOW ]; then
   DESIRED=$((`date +%s -d "$1"` + 24*60*60))
fi

# Kill rtcwake if already running
#sudo killall rtcwake

# Set RTC wakeup time
# N.B. change "mem" for the switchoff option
# find this by "man rtcwake"
sudo rtcwake -m off -t $DESIRED

# feedback
echo "Switching off..."

# give rtcwake some time to make its stuff
sleep 2

# then switchoff
# N.B. dont usually require this bit
#sudo pm-switchoff

# Any commands you want to launch after wakeup can be placed here
# Remember: sudo may have expired by now

# Wake up with monitor enabled N.B. change "on" for "off" if
# you want the monitor to be disabled on wake
#xset dpms force on

# and a fresh console
clear
echo "Lets make some monnaaayyy!!!"
