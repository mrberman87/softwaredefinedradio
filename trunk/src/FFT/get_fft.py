#!/usr/bin/env python

import time, subprocess

def pid_exists(pid):
	try:
		fd = open('/proc/%d/status' % pid, 'r')
		for l in fd:
			if(l.startswith('State:')):
				junk, s, text = l.split( None, 2 )
		fd.close()
		if(s != "Z"):
			return True
		os.waitpid(pid, os.WNOHANG)
		return False
	except IOError, OSError:
		return False

def kill_pid(pid):
	try:
		os.kill(pid, 9)
		return not self.pid_exists(pid)
	except OSError:
		return True

if __name__ == '__main__':
	fft_pid = os.spawnl(os.P_NOWAIT, '/usr/bin/python', 'python', 'FFT_data_aq.py')
	time.sleep(1)
	kill_pid(fft_pid)
	
	subprocess.Popen("octave", stdout=subprocess.PIPE, stdin=subprocess.PIPE).communicate('UAV_fft2\n')
	
	
