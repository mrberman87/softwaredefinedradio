#!/usr/bin/env python
from GPS_getter import GPS_getter
import time

my_getter = GPS_getter()	#initialize gps w/ default value
time.sleep(3)
while True:
	time.sleep(5)	#wait 5 seconds for each query
	my_getter.get_gps('a')	#append to gps.dat file

