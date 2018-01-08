#!/bin/bash

GPU_OVERCLOCK=0
MEM_OVERCLOCK=1050
POWER=110

# ----------------------- Do not edit below this line --------------------------

ps -eaf | grep ethminer | grep 'cuda-parallel-hash' | grep -v -e 'grep' > /dev/null

if [ $? -eq 0 ]; then
  echo "Ethminer-NVIDIA is already running!! Shut it down first before tuning..."
else
  echo "Applying overclock to Nvidia GPUs..."
  echo "==========================================="
  echo "Overclocking GPU Memory to ......... ${MEM_OVERCLOCK}MHz"
  echo "Underclocking GPU Processor to ..... ${GPU_OVERCLOCK}MHz"
  echo "Under-powering to .................. ${POWER}W"
  echo "==========================================="

  GPUS=$(sudo DISPLAY=:0 XAUTHORITY=/var/run/lightdm/root/:0 nvidia-settings -c :0 -q gpus)
  OVERCLOCK_ARGS=""
  for GPU_NUM in $(echo $GPUS | grep -o "\[[0-9]*\]" | grep -o "[0-9]*"); 
  do 
     OVERCLOCK_ARGS="$OVERCLOCK_ARGS --assign [gpu:${GPU_NUM}]/GPUGraphicsClockOffset[3]=${GPU_OVERCLOCK} --assign [gpu:${GPU_NUM}]/GPUMemoryTransferRateOffset[3]=${MEM_OVERCLOCK}"
     
     echo "Applying underpower-limit to Nvidia GPU-$GPU_NUM...."
     sudo nvidia-smi -i ${GPU_NUM} -pl ${POWER}
  done

  echo "Applying overclock settings...."
  sudo DISPLAY=:0 XAUTHORITY=/var/run/lightdm/root/:0 nvidia-settings ${OVERCLOCK_ARGS}
fi

