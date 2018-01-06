#!/usr/bin/env bash

ETHMINER_PATH=/home/shuvo/.ethminer/bin
ACCOUNT_PATH=../.account

if [ ! -d $ETHMINER_PATH ]; then
  echo "No ethminer found at ${ETHMINER_PATH}!"
  exit 1
fi

if [ ! -f $ACCOUNT_PATH ]; then
  echo "No .account file found!! Create one with your <account-hash>.<account-nickname>"
  exit 1
fi

ps -eaf | grep ethminer | grep 'cuda-parallel-hash' | grep -v -e 'grep' > /dev/null
if [ $? -eq 0 ]; then
  echo "Ethminer-NVIDIA is already running!!"
else
  echo "Launching Ethminer-NVIDIA...."
  
  # For fetching list of Nvidia GPUs from headless Ubuntu server
  GPUS=$(sudo DISPLAY=:0 XAUTHORITY=/var/run/lightdm/root/:0 nvidia-settings -c :0 -q gpus)
  GPUS=$(echo $GPUS | grep -o "\[[0-9]*\]" | grep -o "[0-9]*" | tr '\n' ' ')

  ACCOUNT=$(cat ../.account)

  # Use the Cuda drivers for mining
  nohup $ETHMINER_PATH/ethminer \
    --farm-recheck 15000 \
    -SC 2 \
    -RH \
    --cuda-parallel-hash 4 \
    --cuda-schedule sync \
    --cuda-devices $GPUS \
    -U \
    -S us2.ethermine.org:4444 \
    -FS us1.ethermine.org:4444 \
    -O $ACCOUNT \
    >> /var/log/nvidia_miner.log 2>&1 </dev/null & echo $! > /var/log/nvidia_miner.pid & sleep 2
fi
