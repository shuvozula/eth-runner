sudo apt-get update
sudo apt-get upgrade -y

cp provisioner /etc/init.d/provisioner
touch /home/root/init-install
update-rc.d provisioner defaults
sudo reboot

if [ -f /home/root/init-install ]; then
    rm /home/root/init-install
    sudo apt-get install build-essential git \
        mesa-common-dev xorg openbox speedometer \
        python-pip -y
    pip install pipenv

    mkdir -p ~/projects/nvidia-downloads ~/projects/amd-downloads
    sudo touch /var/log/nvidia_miner.log
    sudo touch /var/log/ati_miner.log

    # Download eth-runner
    cd projects/
    git clone https://github.com/shuvozula/eth-runner.git
    cd -

    touch /home/root/install-nvidia-driver
    sudo reboot
fi

#============= resume after reboot ==============

if [ -f /home/root/install-nvidia-driver ]; then
    rm /home/root/install-nvidia-driver

    # Install Cuda for Nvidia, also install the accompanying Nvidia driver 410.48
    cd ~/projects/nvidia-downloads
    wget https://developer.nvidia.com/compute/cuda/10.0/Prod/local_installers/cuda_10.0.130_410.48_linux -O cuda_10.0.130_410.48_linux.run
    sudo chmod +x *.run
    sudo ./cuda_10.0.130_410.48_linux.run
    ----
    ----
    echo "include /usr/local/cuda-10.0/lib64" | sudo tee -a /etc/ld.so.conf.d/cuda.conf
    sudo ldconfig
    echo "export PATH=$PATH:/usr/local/cuda-10.0/bin" >> ~/.bashrc
    echo "export LD_LIBRARY_PATH=/usr/local/cuda-10.0/lib64" >> ~/.bashrc
    source ~/.bashrc

    touch /home/root/configure-nvidia
    sudo reboot
fi

#============= resume after reboot ==============

if [ -f /home/root/configure-nvidia ]; then
    rm /home/root/configure-nvidia

    # checkout eth-runner and configure the NVIDIA GPUs xorg.conf so that nvidia-xconfig can run
    sudo ~/projects/eth-runner/nvidia/enable_nvidia.sh

    # INSTALL NVIDIA DRIVERS
    # Blacklist the Nouveau drivers to let nvidia-xconfig utilize Xorg
    echo "blacklist nouveau" | sudo tee -a /etc/modprobe.d/blacklist-nouveau.conf

    # Start the Xorg server each time on system boot
    sudo mv /etc/rc.local /etc/rc.local.BAK
    sudo cat >> /etc/rc.local << EOF
startx
exit 0
EOF

    touch /home/root/install-amd-driver
    sudo reboot
fi

#============= resume after reboot ==============

if [ -f /home/root/install-amd-driver ]; then
    rm /home/root/install-amd-driver

    # INSTALL AMD DRIVERS
    # get the driver
    cd ~/projects/amd-downloads
    ## --- URL IS NOT DOWNLOADABLE, NEEDS TO BE PRIVATELY HOSTED ---
    wget https://www2.ati.com/drivers/linux/ubuntu/amdgpu-pro-17.20-445420.tar.xz

    # extract and install
    tar -Jxvf amdgpu-pro-17.20-445420.tar.xz
    cd amdgpu-pro-17.20-445420.tar.xz/
    sudo ./amdgpu-pro-install

    # Update user groups and install ROCM component
    sudo usermod -a -G video $LOGNAME
    sudo apt install -y rocm-amdgpu-pro -y
    echo 'export LLVM_BIN=/opt/amdgpu-pro/bin' | sudo tee /etc/profile.d/amdgpu-pro.sh

    sudo apt-get install lm-sensors -y

    touch /home/root/install-ethminer
    sudo reboot
fi

#============= resume after reboot ==============

if [ -f /home/root/install-ethminer ]; then
    rm /home/root/install-ethminer

    # INSTALL ETHMINER
    cd /tmp
    wget https://github.com/ethereum-mining/ethminer/releases/download/v0.17.1-rc.0/ethminer-0.17.1-rc.0-linux-x86_64.tar.gz
    tar xfvz ethminer-0.17.1-rc.0-linux-x86_64.tar.gz
    sudo mv /tmp/bin/* /usr/local/bin/.
    cd -

    # remove the provisioner hook that calls back to this script
    update-rc.d provisioner remove
    rm /etc/init.d/provisioner
fi
