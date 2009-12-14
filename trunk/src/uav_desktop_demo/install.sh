#!/usr/bin/env bash
#
#This install should be ran with sudo
#This will set up everything for the UAV
#

mkdir /uav
mkdir /uav/daemon_pids

cp ~/softwaredefinedradio/src/uav_components/daemon.py /uav/daemon.py
cp ~/softwaredefinedradio/src/uav_components/uav_controller.py /uav/uav_controller.py
cp ~/softwaredefinedradio/src/uav_components/watch_dog1.py /uav/watch_dog1.py
cp ~/softwaredefinedradio/src/uav_components/watch_dog2.py /uav/watch_dog2.py
cp ~/softwaredefinedradio/src/uav_components/wd_reset.py /uav/wd_reset.py
cp ~/softwaredefinedradio/src/uav_components/temp.py /uav/temp.py
cp ~/softwaredefinedradio/src/uav_components/batt.py /uav/batt.py
cp ~/softwaredefinedradio/src/uav_components/uav_utils/GPS_getter.py /uav/GPS_getter.py
cp ~/softwaredefinedradio/src/Data_Path/packetizer.py /uav/packetizer.py
cp ~/softwaredefinedradio/src/Data_Path/dpsk.py /uav/dpsk.py
cp ~/softwaredefinedradio/src/Data_Path/txrx_controller.py /uav/txrx_controller.py
cp ~/softwaredefinedradio/src/FFT/FFT_data_aq.py /uav/FFT_data_aq.py
cp ~/softwaredefinedradio/src/FFT/get_fft.py /uav/get_fft.py
cp ~/softwaredefinedradio/src/FFT/UAV_fft2.m /uav/UAV_fft2.m
#cp ~/softwaredefinedradio/src/uav_components/uav_utils/uav_startup.sh /etc/init.d/uav_startup.sh
#update-rc.d uav_startup.sh defaults
chmod -R 'a'+rw /uav/*
