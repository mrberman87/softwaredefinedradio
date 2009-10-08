#!/usr/bin/env bash

cd ~
apt-get remove -y python-usb
apt-get install -y libusb-dev
svn co https://pyusb.svn.sourceforge.net/svnroot/pyusb pyusb
cd pyusb/trunk/
./setup.py build
./setup.py install
