#!/usr/bin/env bash

#Run with sudo:  sudo ./install_gnuradio.sh

sudo cp /etc/apt/sources.list /etc/apt/sources.list.old

#for the latest stable release
sudo echo deb http://gnuradio.org/ubuntu stable main >> /etc/apt/sources.list
sudo echo deb-src http://gnuradio.org/ubuntu stable main >> /etc/apt/sources.list

#for the latest unstable release
#sudo echo deb http://gnuradio.org/ubuntu unstable main >> /etc/apt/sources.list
#sudo echo deb-src http://gnuradio.org/ubuntu unstable main >> /etc/apt/sources.list

sudo apt-get update
sudo apt-get install --force-yes gnuradio gnuradio-companion
sudo addgroup whoami usrp
