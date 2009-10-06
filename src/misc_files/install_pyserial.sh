#!/usr/bin/env bash

cd ~
svn co https://pyserial.svn.sourceforge.net/svnroot/pyserial pyserial
cd pyserial/trunk/pyserial
python setup.py build
python setup.py install

