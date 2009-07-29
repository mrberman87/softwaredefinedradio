#!/usr/bin/env python

import math
from gnuradio import packet_utils

def conv_integer_to_1_0_string(payload_count):
	# Assumptions: 
	# 1. Each frame starts with packet zero
	# 2. Assuming max number of packets in any frame to be 255
	# 3. Want basic binary representation of the integer

	bin_count = [128, 64, 32, 16, 8, 4, 2, 1]
	r = ['0', '0', '0', '0', '0', '0', '0', '0']

	if payload_count <= sum(bin_count):
		for i in range(0, len(bin_count)):
			if payload_count > bin_count[i] or payload_count == bin_count[i]:
				payload_count = payload_count - bin_count[i]
				r.pop(i)
				r.insert(i, '1')
			elif payload_count == 1:
				r.pop()
				r.append('1')
				break
			elif payload_count == 0:
				break
	return ''.join(r)

def conv_packed_binary_integer_to_1_0_string(passed_payload_count):
	# Assumptions:
	# 1. passed_payload_count is either a string of 1s and 0s or packed binary
	# 2. If passed_payload_count is a packed binary, convert to 1s and 0s string
	# 3. Total packet range (0, 255) or 256 total packets
	# 4. Taking basic binary representation and turning it into equivalent integer

	payload_count = 0
	index = 0
	bin_count = [128, 64, 32, 16, 8, 4, 2, 1]

	if is_1_0_string(passed_payload_count) is False:
		passed_payload_count = conv_packed_binary_string_to_1_0_string(passed_payload_count)
	for ch in passed_payload_count:
		if ch == '1':
			payload_count =	payload_count + bin_count[index]
		index += 1
	return int(payload_count)
