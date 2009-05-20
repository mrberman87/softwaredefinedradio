#!/usr/bin/env python
##############################################################################
'''
to be called from the UAV controller. When this script is called, it saves gps 
location information obtained from gpsd into a text file in the current 
directory of the script.
'''
##############################################################################
import os, telnetlib
HOST='localhost'
PORT='2947'							#2947 is the port for gpsd
gps_file = open('gps.dat','w') 		#(intentionally) overwrite file
tn = telnetlib.Telnet(HOST,PORT)
tn.write("k")
tn.read_until('\n')
#request gps data. see gpsd man pages for details. string is a set of single
#letter commnands.
tn.write("pave\n")
gps_file.write(tn.read_until('\n'))	#save the information returned from gpsd
gps_file.close()
tn.close()
