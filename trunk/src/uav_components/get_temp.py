#!/usr/bin/env python

import serial, os, time

class get_temp:
	def __init__(self):
		s = serial.Serial(0)
		while True:
			s.setRTS(0)
			time.sleep(.0002)
			s.setRTS(1)
			time.sleep(.0008)
