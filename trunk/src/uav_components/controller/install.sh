#!/usr/bin/env bash
#
#This install should be ran with sudo
#This will set up everything for the UAV
#

mkdir /uav
mkdir /uav/daemon_pids

cp ~/softwaredefinedradio/src/uav_components/controller/daemon.py /uav/daemon.py
cp ~/softwaredefinedradio/src/uav_components/controller/uav_controller.py /uav/uav_controller.py
cp ~/softwaredefinedradio/src/uav_components/controller/watch_dog1.py /uav/watch_dog1.py
cp ~/softwaredefinedradio/src/uav_components/controller/watch_dog2.py /uav/watch_dog2.py
cp ~/softwaredefinedradio/src/uav_components/controller/wd_reset.py /uav/wd_reset.py
cp ~/softwaredefinedradio/src/uav_components/get_batt.py /uav/get_batt.py
cp ~/softwaredefinedradio/src/uav_components/get_temp.py /uav/get_temp.py
cp ~/softwaredefinedradio/src/uav_components/GPS_getter.py /uav/GPS_getter.py
cp ~/softwaredefinedradio/src/Data_Path/packetizer.py /uav/packetizer.py
cp ~/softwaredefinedradio/src/Data_Path/tx_rx_path.py /uav/tx_rx_path.py
cp ~/softwaredefinedradio/src/Data_Path/txrx_controller_v2.py /uav/txrx_controller.py
cp ~/softwaredefinedradio/src/FFT/FFT_data_aq.py /uav/FFT_data_aq.py
cp ~/softwaredefinedradio/src/FFT/get_fft.py /uav/get_fft.py
cp ~/softwaredefinedradio/src/FFT/UAV_fft2.m /uav/UAV_fft2.m
#mv /etc/rc.local /etc/rc.local.old
#cp ~/softwaredefinedradio/src/uav_components/rc.local.txt /etc/rc.local
chmod -R 'a'+rw /uav/*
