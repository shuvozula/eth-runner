#!/bin/bash

sudo nvidia-xconfig --enable-all-gpus
sudo nvidia-xconfig -a --cool-bits=28 --allow-empty-initial-configuration
