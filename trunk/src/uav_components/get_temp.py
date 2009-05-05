#!/usr/bin/env python

import timeit, time, serial

def test():
	s = serial.Serial(0)
	#loop while control line is high
	while(s.getCTS()):
		pass
	s.close()

def push_low():
	#put output line low momentarily
	s = serial.Serial(0)
	s.setRTS(1)
	time.sleep(.001)
	s.setRTS(0)
	s.close()

def decode_data(value):
	#...

if __name__=='__main__':
	push_low()
	t=timeit.Timer('test()', "from __main__ import test")
	fd = open('temp.dat', "w")
	fd.write(decode_data(100*t.timeit(number=10)))
	fd.close()

