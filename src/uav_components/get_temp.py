#!/usr/bin/env python

import timeit, time, serial

def test():
	s = serial.Serial(0)
	push_low(s)
	#loop while control line is high
	while(s.getCTS()):
		pass
	s.close()

def push_low(s):
	#put output line low momentarily
	s.setRTS(1)
	time.sleep(.001)
	s.setRTS(0)

def decode_data(value):
	#...

if __name__=='__main__':
	t=timeit.Timer('test()', "from __main__ import test")
	fd = open('temp.dat', "w")
	fd.write(decode_data(t.timeit(number=1)))
	fd.close()

