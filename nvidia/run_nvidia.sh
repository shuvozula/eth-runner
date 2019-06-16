#!/bin/bash

my_dir="$(dirname $0)"

# If running using start.sh
if [ ! -f $my_dir/../init.sh ]; then
  echo "init.sh not found!!!"
  exit 1
else
  . $my_dir/../init.sh
fi


ps -eaf | grep ethminer | grep 'cuda-parallel-hash' | grep -v -e 'grep' > /dev/null
if [ $? -eq 0 ]; then
  echo "Ethminer-NVIDIA is already running!!"
else
  echo "Launching Ethminer-NVIDIA...."

  # For fetching list of Nvidia GPUs from headless Ubuntu server
  GPUS=$(sudo DISPLAY=:0 XAUTHORITY=/var/run/lightdm/root/:0 nvidia-settings -c :0 -q gpus)
  GPUS=$(echo $GPUS | grep -o "\[[0-9]*\]" | grep -o "[0-9]*" | tr '\n' ' ')

  # Use the Cuda drivers for mining
  nohup $ETHMINER_PATH/ethminer \
    --pool stratum://$ACCOUNT.miner@us1.ethpool.org:3333 \
    --cuda \
    --report-hashrate \
    --farm-recheck 15000 \
    --display-interval 30 \
    --cuda-parallel-hash 4 \
    --cuda-schedule sync \
    --cuda-devices $GPUS \
    --dag-load-mode 1 \
    >> /var/log/nvidia_miner.log 2>&1 </dev/null & echo $! > /var/log/nvidia_miner.pid & sleep 2
fi
