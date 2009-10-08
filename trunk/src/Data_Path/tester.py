#!/usr/bin/env python

from txrx_controller_v2 import txrx_controller
import time

tb = txrx_controller(version = 'qpsk')
time.sleep(2)
temp = tb.transmit('/data.txt')
#temp = tb.receive()
print temp

"""
temp = True
commands = ['picture', 'FFT', 'telemetry', 'battery', 'temperature']
index = 0
counter = 0
while temp:
	temp = tb.transmit(commands[index])
	index += 1
	if index == 5:
		index = 0
	counter += 1
	if counter == 10:
		temp = False
"""

"""
def main():
	data = raw_input("Asking for input: ")
	if data == '1':
		return True
	else:
		data2 = data
"""
"""
def spc(data):
	payload_count = []
	payload = ''
	loc = 1
	for ch in data:
		if ch == ':':
			payload = data[loc:]
			break
		else:
			payload_count.append(ch)
		loc += 1
	print "Payload Count: ", ''.join(payload_count), "Payload: ", payload
"""
