#!/bin/bash

DEFAULT_GPU_OVERCLOCK=0
DEFAULT_MEM_OVERCLOCK=1000
DEFAULT_POWER=110

# each Map index is the GPU index as discovered by "ethminer --list-devices -G".
# Tune parameter values are stored in the order: GPU_OVERCLOCK;MEMORY_OVERCLOCK;POWER_UNDERCLOCK
declare -A TUNE_MAP_OVERRIDE=(
    [2]='0;1200;110'
)

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
  echo "=================================================="

  GPUS=$(sudo DISPLAY=:0 XAUTHORITY=/var/run/lightdm/root/:0 nvidia-settings -c :0 -q gpus)
  OVERCLOCK_ARGS=""
  for GPU_NUM in $(echo $GPUS | grep -o "\[[0-9]*\]" | grep -o "[0-9]*");
  do
     if [[ ${TUNE_MAP_OVERRIDE[${GPU_NUM}]+ispresent} ]]; then
        IFS=';' read -r -a TUNE_PARAMS <<< "${TUNE_MAP_OVERRIDE[$GPU_NUM]}"
        OVERCLOCK_ARGS="$OVERCLOCK_ARGS --assign [gpu:${GPU_NUM}]/GPUGraphicsClockOffset[3]=${TUNE_PARAMS[0]} --assign [gpu:${GPU_NUM}]/GPUMemoryTransferRateOffset[3]=${TUNE_PARAMS[1]}"
        POW="${TUNE_PARAMS[2]}"
     else
        OVERCLOCK_ARGS="$OVERCLOCK_ARGS --assign [gpu:${GPU_NUM}]/GPUGraphicsClockOffset[3]=${DEFAULT_GPU_OVERCLOCK} --assign [gpu:${GPU_NUM}]/GPUMemoryTransferRateOffset[3]=${DEFAULT_MEM_OVERCLOCK}"
        POW=${DEFAULT_POWER}
     fi
     echo "Applying underpower-limit to Nvidia GPU-$GPU_NUM...."
     sudo nvidia-smi -i ${GPU_NUM} -pl ${POW}
  done

  echo "Applying overclock settings...."
  sudo DISPLAY=:0 XAUTHORITY=/var/run/lightdm/root/:0 nvidia-settings ${OVERCLOCK_ARGS}
fi
