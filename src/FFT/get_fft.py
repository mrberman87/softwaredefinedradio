#!/usr/bin/env python

import subprocess, os, sys, time

if __name__ == '__main__':
	try:
		if sys.argv[1] is None:
			real_path = os.getcwd() + '/real'
		else:
			real_path = sys.argv[1]
	except: 
		real_path = os.getcwd() + '/real'
	
	try:
		if sys.argv[2] is None:
			imag_path = os.getcwd() + '/imaginary'
		else:
			imag_path = sys.argv[2]
	except:
		imag_path = os.getcwd() + '/imaginary'

	try:
		if sys.argv[3] is None:
			fc = str(440e6)
		else:
			fc = sys.argv[3]
	except: 
		fc = str(440e6)

	try:
		if sys.argv[4] is None:
			to_path = os.getcwd() + '/fft.png'
		else:
			to_path = sys.argv[4]
	except: 
		to_path = os.getcwd() + '/fft.png'

	#FIXME add the sys.argv[#] statements back to the subprocess call below
	#to allow for variable file paths for both the real and imaginary USRP data
	p = subprocess.Popen('python FFT_data_aq.py %s %s %s' % (real_path, imag_path, fc), shell=True)
	os.waitpid(p.pid, 0)
	p = subprocess.Popen("octave", stdin=subprocess.PIPE, shell=True)
	os.write(p.stdin.fileno(), 'UAV_fft2(\'%s\',\'%s\',\'%s\')\n' % (real_path, imag_path, to_path))
	time.sleep(1)
	p.wait()

