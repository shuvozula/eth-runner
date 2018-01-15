#!/bin/bash

AMD_OPENCL_PLATFORM_ID=0

# ----------------------- Do not edit below this line --------------------------

my_dir="$(dirname $0)"

# If running using start.sh
if [ ! -f $my_dir/../init.sh ]; then
  echo "init.sh not found!!!"
  exit 1
else
  . $my_dir/../init.sh
fi


ps -eaf | grep ethminer | grep 'opencl-platform 0' | grep -v -e 'grep' > /dev/null
if [ $? -eq 0 ]; then
  echo "Ethminer-ATI is already running."
else
  echo "Launching Ethminer-ATI...."

  nohup $ETHMINER_PATH/ethminer \
    --farm-recheck 15000 \
    -SC 2 \
    --opencl-platform $AMD_OPENCL_PLATFORM_ID \
    -RH \
    -G \
    -S us2.ethermine.org:4444 \
    -FS us1.ethermine.org:4444 \
    -O $ACCOUNT \
    >> /var/log/ati_miner.log 2>&1 </dev/null & echo $! > /var/log/ati_miner.pid & sleep 2
fi
