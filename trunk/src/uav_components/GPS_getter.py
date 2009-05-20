#!/usr/bin/env python
##############################################################################
'''
An instance of this class opens gpsd, and can then be used to write current
GPS data into a file. currently, assumes gpsd is not running. could operate
unexpectedly if gpsd is already running.
'''
##############################################################################
import os,telnetlib, time

class GPS_getter:
	def __init__(self, HOST = 'localhost', PORT = '2947'):
		#open gpsd to and prepare to read GPS device
		os.system("gpsd /dev/ttyUSB0" + " -S " + PORT)

		#os.system("gpsfake dl_gps.txt")

		#open a telnet session to talk to gpsd
		self.tn = telnetlib.Telnet(HOST, PORT)
		#immediately query gpsd, because it will not bind to a GPS until
		#it receive's its first query.
		self.tn.write("p\n")
		self.tn.read_until("\n")

	def get_gps(self, write_opt = 'w'):
		#this method writes asks gpsd for info, then writes that info
		#to a specified file. 'w' overwrites the file, and 'a' appends to it.
		#issue the single letter queries for data to gpsd
		self.tn.write("pave\n")
		#read gpsd's response to queries
		loc_data = self.tn.read_until("\n")
		#default is to (intentionally) overwrite file
		gps_file = open('gps.dat',write_opt)
		#save the information returned from gpsd
		gps_file.write(loc_data)
		gps_file.close()

