#!/usr/bin/env python

import os
import time

read_file = "test.dat"
write_file = "test1.dat"
last_mod = time.localtime()

while True:
	#do nothing while the last time the file was modified is before
	#the time we have as its last modified time
	while (time.localtime(os.path.getmtime(read_file)) <= last_mod):
		temp = 0
	
	#read in command and prepare string to be executed on the system
	f_read = open(read_file, "r")
	os.system(f_read.readline().strip("\n") + " > " + write_file)
	f_read.close()
	
	last_mod = time.localtime(os.path.getmtime(read_file))

