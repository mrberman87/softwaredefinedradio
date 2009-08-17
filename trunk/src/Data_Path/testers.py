#!/usr/bin/env python

from txrx_controller import txrx_controller
tb = txrx_controller()
tb.transmit("Hello")



"""
data_o = ['Event', 'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
bad_pkt_indexes = ['3', '8', '1', '18', '12', '5', '19']
print bad_pkt_indexes
for i in range(len(bad_pkt_indexes)):
	print data_o[int(bad_pkt_indexes[i])]
temp = data_o[3]
print temp
"""

"""
data_o = ['Event', 'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
data = ['', '','','','','','','','','','','','','','','', '', '', '', '', '', '', '', '', '', '', '']
index = 1
data_temp = list()
bad_pkt_indexes = list()
index = 0
n_index = 0
while len(bad_pkt_indexes) < data.count(''):
	index = data.index('', n_index)
	bad_pkt_indexes.append(str(index))
	n_index = index + 1

total_pkts = len(bad_pkt_indexes) + 1
data_temp.append(str(total_pkts) + ':' + '0' + ':' + 'PR')
for i in bad_pkt_indexes:
	data_temp.append(str(total_pkts) + ':' + str(i) + ':' + data_o[int(i)])

for i in range(1, len(data_temp)):
	temp = data_temp.pop(1)
	temp = temp[temp.index(":") + 1:]
	pkt_count = int(temp[:temp.index(":")])
	payload = temp[temp.index(":") + 1:]
	data.pop(pkt_count)
	data.insert(pkt_count, payload)
	index += 1

print data
"""

"""
temp_index
data_temp = ['Event', 'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
data = list()
data_2 = list()
temp_index = data_temp[0]
for i in range(len(data_temp)):
	data.append(data_temp[i])
for i in range(len(data_temp)):
	data_2.append(data_temp.pop(0))
print data
print data_temp
print data_2
"""

"""
data = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
temp = ':'.join(data)
print temp
temp_0 = temp.split(':')
print temp_0
"""

"""
data = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
for i in range(len(data)):
	print i
"""

"""
data = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o', 'p', 'q', 'r', 's', 't', 'u']
data_temp = ''.join(data)
pkts = list()
payload_length = 2
index = 0
total_pkts = len(data_temp)/payload_length + 2
if len(data)%2 == 0:
	total_pkts -= 1
pkts.append(str(total_pkts) + ':EW:' + '0')
for i in range(1, total_pkts):
	payload = data_temp[:payload_length]
	data_temp = data_temp[payload_length:]
	pkts.append(str(total_pkts) + ':' + payload + ':' + str(i))

print pkts
"""

"""
data = ['', 'a', '', 'b']
pkt_count = 6
total_pkts = 7
payload = 'Next Test'
while len(data) < pkt_count:
	data.append('')

data.append(payload)
print data
print len(data)
if len(data) == total_pkts:
	print "Got last Packet"
"""

"""
data_temp = list()
for i in range(len(data)):
	data_temp.append(data[i])

print "DATA: ",data
print "data_temp: ",data_temp
data_temp.pop(0)
print "DATA: ",data
print "data_temp: ",data_temp
"""

"""
temp = data
bad_packet_indexes = list()
index = 0
n_index = 0
while len(bad_packet_indexes) < data.count(''):
	index = data.index('', n_index)
	n_index = index + 1
	bad_packet_indexes.append(str(index))
print bad_packet_indexes
print ':'.join(bad_packet_indexes)
"""

"""
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
