#!/usr/bin/env python
##############################################################################
'''
An instance of this class opens gpsd, and can then be used to write current
GPS data into a file.
'''
##############################################################################
import os,telnetlib, time,subprocess

class GPS_getter:
	def __init__(self, HOST = 'localhost', PORT = '2947'):
		#attempts to start gpsd are silently ignored it is already running
		#so we need to kill it if already being started
		self.kill_gpsd()
		
		#open gpsd to and prepare to read GPS device
		os.system("gpsd /dev/ttyUSB0 -S " + PORT)
		#os.system("gpsfake dl_gps.txt") #uncomment gpsfake call if testing
		
		#delay opening a telnet session to give gpsd time to set GPS device
		time.sleep(2)

		#open a telnet session to talk to gpsd
		self.tn = telnetlib.Telnet(HOST, PORT)
		#immediately query gpsd, because it will not bind to a GPS until
		#it has received its first query.
		self.tn.write("p\n")
		self.tn.read_until("\n")

	def get_gps(self, write_opt = 'w', path = 'gps.dat'):
		#this method writes asks gpsd for info, then writes that info
		#to a specified file. 'w' overwrites the file, and 'a' appends to it.
		#issue the single letter queries for data to gpsd
		#p = pos, a = alt, v = velocity, e = error
		self.tn.write("pave\n")
		#read gpsd's response to queries
		loc_data = self.tn.read_until("\n")
		#default is to (intentionally) overwrite file
		gps_file = open(path,write_opt)
		#save the information returned from gpsd
		gps_file.write(loc_data)
		gps_file.close()

	def kill_gpsd(self):
		#this method will kill any currently running instances of gpsd.
		bufsize = 256
		cmd = "pidof gpsd\n"
		#pidof prints the pid of the given program to the stdout
		pipe = subprocess.Popen(cmd, shell = True,
								bufsize = bufsize,
								stderr = subprocess.PIPE,
								stdout = subprocess.PIPE)

		[pid,errors] = pipe.communicate() #read the stdout and stderr of pidof
		if pipe.returncode == 0: 
			"""a return code of 0 means no errors occured, so there IS
			 an instance of gpsd running"""
			kill_cmd = "kill -KILL " + pid
			pipe2 = subprocess.Popen(kill_cmd, shell = True, bufsize = bufsize)

