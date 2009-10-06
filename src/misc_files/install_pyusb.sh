#!/usr/bin/env bash

cd ~
apt-get remove -y python-usb
svn co https://pyusb.svn.sourceforge.net/svnroot/pyusb pyusb
cd pyusb/trunk/
./setup.py build
./setup.py install
