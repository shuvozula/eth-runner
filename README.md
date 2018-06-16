# Eth-Runner

Runs ethminer with all available Nvidia and AMD GPUs. This was tested on a system using Ubuntu 16.04LTS, containing the following specs:
- ASUS B250 Mining Expert
- 8 x GTX 1070 / 8GB GPUs
- 4 x AMD RX580 / 8GB GPUs.
- I7 core
- 32GB RAM
- 1TB Samsung SSD (for fast read/write)

Note: AMD GPUs were recorded as opencl-platform with value `0`. It could be different for your system. So check by running `ethminer --list-devices` and look for the platform-id in the output for AMD (Ellesmere), usually it is 0.

## Features:
- For Nvidia cards, tunes them by undervolting GPU and increasing memory frequency, increasing mining to 30MH/s+ for Eth
- For AMD cards, the BIOS need to be flashed using [Polaris Bios Editor](https://github.com/jaschaknack/PolarisBiosEditor).

## Prerequisites:
- Create a `.account` file that contains the Ethereum account alphanumeric string and nickname, like this: `<account-address>.<nickname>` and put it in the root folder of this project.
- nvidia-smi (comes with Nvidia drivers)
- nvidia-xconfig (comes with Nvidia drivers)
- Install [ethminer](https://github.com/ethereum-mining/ethminer). Make sure `ethminer --list-devices` recognizes all your GPUs and lists them. Pay attention to the platform-IDs for AMD cards as that's required in the `amd/run_amd.sh` script.

## Usage:
- Clone the repo.
- Edit `init.sh` and add the location for Ethminer in `ETHMINER_PATH`, eg: `/home/foobar/.ethminer/bin`
- Set the tune parameters for Nvidia tuning in `nvidia/tune_nvidia.sh`. The default values should fetch 30MH/s on Nvidia 1070 GTX 8GB, but feel free to tweak that even further with higher `MEM_OVERCLOCK` values and higher `POWER` values.
- No AMD tuning is provided here, you have to use [Polaris Bios Editor](https://github.com/jaschaknack/PolarisBiosEditor) to flash the ROM and get your optimal hashrate. A list of available pre-tested ROMS for MSI RX580 8GB cards are provided in `rom/` for use, *but use it at your own risk as not every GPU is the same*.
- Edit `amd/run_amd.sh` and set the platform-ID for AMD cards fetched using `ethminer --list-devices`
- Start mining by runing `sudo start.sh`, which will first enable and tune your Nvidia cards and then will run ethminer on all available Nvidia and AMD GPUs.

## Crontab
The `start.sh`, `stop.sh` and `switchoff_until.sh` scripts can be used with crontab as shown below, which wakes up your miner everyday at 10pm local time and starts mining at 10:05pm local time. Then kills all processes and shuts-down at 8:02am the next day:
```
# m h  dom mon dow   command

# Start miners and watchdog
@reboot sudo /path/to/eth-runner/start.sh > /path/to/eth-runner/logs/start.log 2>&1

# Shutdown at 7am everyday
00 07 * * * sudo /path/to/eth-runner/stop.sh
02 07 * * * sudo /path/to/eth-runner/shutdown.sh
```
