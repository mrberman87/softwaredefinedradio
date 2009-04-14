#!/usr/bin/env python

#File Parser to parse the FFT data. The file contains the time
#domain waveform directly from the signal source. It is dumped
#into the file using the pickle library commands. 

#Reference Material for file read and write commands and parsing
#commands from Programming Python Pg. 145 and Pg. 1337

#BY Charles Judah 4/1/2009

import os, sys

FFT_tdata = open('Crap.dat', 'r')
FFT_appended = open('FFT.dat', 'wb')

for line in FFT_tdata.readlines():

	if line.startswith('F'):
		appended = line.replace('F', '')
	if line.startswith('tp0'):
		appended = line.replace('tp0', '')
	if line.startswith('.'):
		appended = line.replace('.', '')
	if line.startswith('('):
		appended = line.replace('(F', '')
	#if line.endswith('\n'):
		#appended = appended.replace('\n', '')
	FFT_appended.write(appended)
FFT_tdata.close()

