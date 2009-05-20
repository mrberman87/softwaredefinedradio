#!/usr/bin/env python
##############################################################################
#initializes gpsd to read the GPS 18 module on a USB port.
##############################################################################
import os,sys
command = "gpsd /dev/ttyUSB"
dev_num = 0					#depends on which port the device is connected to
PORT = '2947'
#SYS_CALL_ERROR = '256'
#SYS_CALL_SUCCESS = '0'

os.system(command + str(dev_num) + " -S " + PORT)
	
#gpsd does not start polling until it has at least one request
#so request once, then clean up
os.system("./get_gps.py")
os.system("rm gps.dat")
