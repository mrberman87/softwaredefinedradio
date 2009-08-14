#!/usr/bin/env python

def main():
	data = raw_input("Asking for input: ")
	if data == '1':
		return True
	else:
		data2 = data

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
