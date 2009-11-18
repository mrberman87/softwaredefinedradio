#!/usr/bin/env python

#import ns
import packetizer
#from gnuradio import gr

"""
msgs = gr.message_source(gr.sizeof_char, 5)
test = "Testing how this works."
msgs.msgq().insert_tail(gr.message_from_string(test))
print msgs.msgq().delete_head().to_string()
"""

file_name = '/home/sab/Desktop/payload_transmit_path.py'
fd = open(file_name, 'r')
file_length = len(fd.read())
fd.close()
fd = open(file_name, 'r')
payload_count = 0
byte_count = 0
for i in range(0, int(file_length/1024) + 1):
	payload=fd.read(1024)
	packetizer.make_packet(payload, payload_count=i)
	byte_count += len(payload)
	print "Byte Count: ", byte_count, " Payload Count: ", i
fd.close()

"""
test = ns.conv_integer_to_1_0_string(0)
print '\x55'
(testing, ignore) = packet_utils.conv_1_0_string_to_packed_binary_string(test)
ns.pbit10s(')
"""

"""
for i in range(0, 256):
	test = packetizer.conv_integer_to_1_0_string(i)
	print "i: ", i
	test_0 = packetizer.conv_packed_binary_integer_to_1_0_string(test)
	print "E: ", test_0
"""

"""
fd = open('/home/sab/Desktop/payload_transmit_path.py', 'r')
data = fd.read(1024)
fd.close()

print len(data)
"""
