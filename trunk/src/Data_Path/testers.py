#!/usr/bin/env python

data = ['a', 'b', 'a', 'b', 'a', 'b', 'a', 'b']
bad_packet_indexes = list()
index = 0
while len(bad_packet_indexes) < data.count('b'):
	index = data.index('b', index + 1)
	bad_packet_indexes.append(str(index))	
print bad_packet_indexes
for i in bad_packet_indexes:
	print data[int(i)] + i
"""
from gnuradio import gr

msg = gr.message_source(gr.sizeof_char*1)
msgq = msg.msgq()
testing = msgq.delete_head_nowait()

print testing
try:
	msgq.delete_head_nowait()
except:
	print "Testing"
"""

"""
import queue

tb = queue.queue()

tb.add("Hello")
tb.add("m effin")
tb.add("world")
tb.add("!")

tb.print_q()

tb.order(2, 0)

tb.print_q()

testing = tb.delete_head()

print testing

tb.print_q()

size = tb.size()

print size

"""
"""

import packetizer

testings = ''
for i in range(0, 256):
	print "Packet Count: ", i
	test = packetizer.make_packet(" |_| ",i)
"""
