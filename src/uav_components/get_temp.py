#!/usr/bin/env python

import timeit, time, serial

def test():
	s = serial.Serial(0)
	push_low(s)
	#loop while control line is high
	while(not s.getCTS()):
		pass
	s.close()

def push_low(s):
	#put output line low momentarily
	s.setRTS(1)
	time.sleep(.001)
	s.setRTS(0)

def decode_data(value1):
	#out = -60.732*value*value*value + 345.5*value*value - 836.16*value + 380
	out=549.69*value1*value1 - 1194.4*value1 + 439.13		
	print "%d degrees" % out
	print value1
if __name__ == '__main__':
	t=timeit.Timer('test()', "from __main__ import test")
	while(True):
		decode_data(t.timeit(number=1))
		time.sleep(1)
	
	#fd = open('temp.dat', "w")
	#fd.write(decode_data(t.timeit(number=1)))
	#fd.close()

