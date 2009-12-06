#!/usr/bin/env python

import subprocess, os, sys, time

if __name__ == '__main__':
	real_path = os.getcwd() + '/real'
	imag_path = os.getcwd() + '/imaginary'
	to_path = os.getcwd() + '/fft.png'

	try:
		if sys.argv[1] is None:
			fc = str(440e6)
		else:
			fc = sys.argv[3]
	except: 
		fc = str(440e6)

	p = subprocess.Popen('python FFT_data_aq.py %s %s %s' % (real_path, imag_path, fc),stdout=open(os.devnull,'w') shell=True)
	time.sleep(1)
	p.wait()
	p = subprocess.Popen("octave", stdin=subprocess.PIPE, shell=True)
	os.write(p.stdin.fileno(), 'UAV_fft2(\'%s\',\'%s\',\'%s\')\n' % (real_path, imag_path, to_path))
	time.sleep(1)
	p.wait()

