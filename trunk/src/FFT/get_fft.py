#!/usr/bin/env python

import subprocess, os, sys, time

if __name__ == '__main__':
	to_path = sys.argv[1]
	from_path = sys.argv[2]
	p = subprocess.Popen('> %s' % path, shell=True)
	p.wait()
	p = subprocess.Popen('python FFT_data_aq.py', shell=True)
	os.waitpid(p.pid, 0)
	p = subprocess.Popen("octave", stdin=subprocess.PIPE, shell=True)
	os.write(p.stdin.fileno(), 'UAV_fft2 %s %s\n' % (to_path, from_path))
	time.sleep(5)
	os.write(p.stdin.fileno(), 'exit\n')
