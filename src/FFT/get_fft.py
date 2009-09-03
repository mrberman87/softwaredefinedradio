#!/usr/bin/env python

import subprocess

if __name__ == '__main__':
	os.spawnl(os.P_WAIT, '/usr/bin/python', 'python', 'FFT_data_aq.py')
	subprocess.Popen("octave", stdout=subprocess.PIPE, stdin=subprocess.PIPE).communicate('UAV_fft2\n')

