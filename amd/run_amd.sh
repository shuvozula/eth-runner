#!/usr/bin/env bash

ETHMINER_PATH=/home/shuvo/.ethminer/bin
ACCOUNT_PATH=../.account
OPENCL_PLATFORM_ID=0

if [ ! -d $ETHMINER_PATH ]; then
  echo "No ethminer found at ${ETHMINER_PATH}!"
  exit 1
fi

if [ ! -f $ACCOUNT_PATH ]; then
  echo "No .account file found!! Create one with your <account-hash>.<account-nickname>"
  exit 1
fi

ps -eaf | grep ethminer | grep 'opencl-platform 0' | grep -v -e 'grep' > /dev/null

if [ $? -eq 0 ]; then
  echo "Ethminer-ATI is already running."
else
  echo "Launching Ethminer-ATI...."

  ACCOUNT=$(cat ../.account)

  nohup $ETHMINER_PATH/ethminer \
    --farm-recheck 15000 \
    -SC 2 \
    --opencl-platform $OPENCL_PLATFORM_ID \
    -RH \
    -G \
    -S us2.ethermine.org:4444 \
    -FS us1.ethermine.org:4444 \
    -O $ACCOUNT \
    >> /var/log/ati_miner.log 2>&1 </dev/null & echo $! > /var/log/ati_miner.pid & sleep 2
fi
