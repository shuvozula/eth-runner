#!/bin/bash

sudo apt-get install build-essential git mesa-common-dev \
		xorg openbox speedometer -y

cd /tmp
wget https://github.com/ethereum-mining/ethminer/releases/download/v0.17.1-rc.0/ethminer-0.17.1-rc.0-linux-x86_64.tar.gz
tar xfvz ethminer-0.17.1-rc.0-linux-x86_64.tar.gz
sudo mv /tmp/bin/* /usr/local/bin/.
sudo chmod +x /usr/local/bin/ethminer
cd -

export ETHMINER_PATH=/usr/local/bin/
