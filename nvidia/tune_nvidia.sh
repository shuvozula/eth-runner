#!/bin/bash

DEFAULT_GPU_OVERCLOCK=0
DEFAULT_MEM_OVERCLOCK=1000
DEFAULT_POWER=110

# Declare separate settings for individual GPUs here

# declare GPU settings for 1060 6GB GPU
declare -A GPU_1060_TUNE_MAP
GPU_1060_TUNE_MAP[GPU]=0
GPU_1060_TUNE_MAP[MEM]=1200
GPU_1060_TUNE_MAP[POW]=110

TUNE_MAP[2]=GPU_1060_TUNE_MAP


# ----------------------- Do not edit below this line --------------------------

ps -eaf | grep ethminer | grep 'cuda-parallel-hash' | grep -v -e 'grep' > /dev/null

if [ $? -eq 0 ]; then
  echo "Ethminer-NVIDIA is already running!! Shut it down first before tuning..."
else
  echo "Applying overclock to Nvidia GPUs..."
  echo "=================================================="
  echo "Default Overclocking GPU Memory to ......... ${DEFAULT_MEM_OVERCLOCK}MHz"
  echo "Default Underclocking GPU Processor to ..... ${DEFAULT_GPU_OVERCLOCK}MHz"
  echo "Default Under-powering to .................. ${DEFAULT_POWER}W"
  echo ""
  echo "<<1060 Tune Settings>>"
  echo "1060 Overclocking GPU Memory to ......... ${GPU_1060_TUNE_MAP[GPU]}MHz"
  echo "1060 Underclocking GPU Processor to ..... ${GPU_1060_TUNE_MAP[MEM]}MHz"
  echo "1060 Under-powering to .................. ${GPU_1060_TUNE_MAP[POW]}W"
  echo "=================================================="

  GPUS=$(sudo DISPLAY=:0 XAUTHORITY=/var/run/lightdm/root/:0 nvidia-settings -c :0 -q gpus)
  OVERCLOCK_ARGS=""
  for GPU_NUM in $(echo $GPUS | grep -o "\[[0-9]*\]" | grep -o "[0-9]*");
  do
     if [ ${TUNE_MAP[${GPU_NUM}]+ispresent} ]; then
        OVERCLOCK_ARGS="$OVERCLOCK_ARGS --assign [gpu:${GPU_NUM}]/GPUGraphicsClockOffset[3]=${TUNE_MAP[${GPU_NUM}][GPU]} --assign [gpu:${GPU_NUM}]/GPUMemoryTransferRateOffset[3]=${TUNE_MAP[${GPU_NUM}][MEM]}"
        POW="${TUNE_MAP[${GPU_NUM}][POW]}"
     else
        OVERCLOCK_ARGS="$OVERCLOCK_ARGS --assign [gpu:${GPU_NUM}]/GPUGraphicsClockOffset[3]=${DEFAULT_GPU_OVERCLOCK} --assign [gpu:${GPU_NUM}]/GPUMemoryTransferRateOffset[3]=${DEFAULT_MEM_OVERCLOCK}"
        POW=${DEFAULT_POWER}
     fi
     echo "Applying underpower-limit to Nvidia GPU-$GPU_NUM...."
     sudo nvidia-smi -i ${GPU_NUM} -pl ${DEFAULT_POWER}
  done

  echo "Applying overclock settings...."
  sudo DISPLAY=:0 XAUTHORITY=/var/run/lightdm/root/:0 nvidia-settings ${OVERCLOCK_ARGS}
fi
