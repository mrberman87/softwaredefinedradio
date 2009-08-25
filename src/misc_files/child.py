#!/usr/bin/env python

import time, sys

if __name__ == '__main__':
	tmp = sys.stdin.read()
	if tmp == '':
		print "nothing\n"
	else:
		print tmp + "\n"

