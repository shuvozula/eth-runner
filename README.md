# Eth-Runner

Runs ethminer on all available Nvidia and AMD GPUs. This was tested on a system containing the following specs:
- ASUS B250 Mining Expert
- 8 x GTX 1070 / 8GB GPUs
- 4 x AMD RX580 / 8GB GPUs.
- 1TB Samsung SSD (for fast read/write)

Note: AMD GPUs were recorded as opencl-platform with value `0`. It could be different for your system. So check by running `ethminer --list-devices` and look for the platform-id in the output for AMD (Ellesmere), usually it is 0.

## Features:
- For Nvidia cards, tunes them by undervolting GPU and increasing memory frequency, increasing mining to 30MH/s+ for Eth
- For AMD cards, the BIOS need to be flashed using [Polaris Bios Editor](https://github.com/jaschaknack/PolarisBiosEditor).
- Comes with code snippets for Terminator terminal for Ubuntu/Linux to make layout using *sensors* to watch AMD temp and nvidia-smi to watch NVIDIA card watts, temp, memory usage, etc.

## Usage
Clone and run `sudo start.sh`, which will first enable and tune your Nvidia cards and then will run ethminer on all Nvidia and AMD GPUs.
