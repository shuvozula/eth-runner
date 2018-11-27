#!/bin/bash

sudo nvidia-xconfig --enable-all-gpus
sudo nvidia-xconfig -a --cool-bits=31 --allow-empty-initial-configuration
