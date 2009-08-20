#!/usr/bin/env bash

mkdir /uav
mkdir /uav/daemon_pids

cp ~/softwaredefinedradio/src/uav_components/controller/controls.py /uav/controls.py
cp ~/softwaredefinedradio/src/uav_components/controller/daemon.py /uav/daemon.py
cp ~/softwaredefinedradio/src/uav_components/controller/timeout.py /uav/timeout.py
cp ~/softwaredefinedradio/src/uav_components/controller/uav_controller.py /uav/uav_controller.py
cp ~/softwaredefinedradio/src/uav_components/controller/watch_dog1.py /uav/watch_dog1.py
cp ~/softwaredefinedradio/src/uav_components/controller/watch_dog2.py /uav/watch_dog2.py
cp ~/softwaredefinedradio/src/uav_components/get_batt.py /uav/get_batt.py
cp ~/softwaredefinedradio/src/uav_components/get_temp.py /uav/get_temp.py
cp ~/softwaredefinedradio/src/uav_components/get_gps.py /uav/get_gps.py
cp ~/softwaredefinedradio/src/Data_Path/packetizer.py /uav/packetizer.py
cp ~/softwaredefinedradio/src/Data_Path/tx_rx_path.py /uav/tx_rx_path.py
cp ~/softwaredefinedradio/src/Data_Path/txrx_controller.py /uav/txrx_controller.py
mv /etc/rc.local /etc/rc.local.old
cp ~/softwaredefinedradio/src/uav_components/rc.local.txt /etc/rc.local
