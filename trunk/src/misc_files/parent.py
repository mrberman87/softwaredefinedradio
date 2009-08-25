#!/usr/bin/env python

import time, subprocess

if __name__ == '__main__':
	pipe = subprocess.PIPE
	p = subprocess.Popen(['python', './child.py'], shell=False, stdin=pipe, stdout=pipe, stderr=pipe, close_fds=True)
	time.sleep(1)
	p.stdin.write("hello\n")
	test = True
	while test:
		tmp = p.stdout.read()
		if tmp != '':
			test = False
	print tmp

