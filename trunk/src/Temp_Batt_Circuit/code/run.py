#!/usr/bin/env python

import time, subprocess

if __name__ == '__main__':
	while(True):
		p = subprocess.Popen("python batt.py", shell=True)
		p.wait()
		p = subprocess.Popen("python temp.py", shell=True)
		p.wait()
		time.sleep(.5)

