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
	fnull = open(os.devnull, 'w')
	p = subprocess.Popen('python FFT_data_aq.py %s %s %s' % (real_path, imag_path, fc), shell=True)
	time.sleep(1)
	p.wait()
	p = subprocess.Popen("octave", stdin=subprocess.PIPE, stdout = fnull, shell=True)
	os.write(p.stdin.fileno(), 'UAV_fft2(\'%s\',\'%s\',\'%s\')\n' % (real_path, imag_path, to_path))
	time.sleep(1)
	p.wait()
	fnull.close()
