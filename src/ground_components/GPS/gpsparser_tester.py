#!/usr/bin/env python
'''
'''

from gpsparser import gpsparser


my_file=open('gpsd_strings.txt','r');  #open file for reading
my_line_queue=list()    
for line in my_file.readlines():
    my_line_queue.append(line)


my_file.close();    #close file handle so other proceses can access it

my_parser=gpsparser('my_log.txt')

for item in my_line_queue:
	my_parser.update_packet(item)
	my_packet=my_parser.current_packet
	print "altitude:\t", my_packet.alt,"m"
	print "longitude:\t", my_packet.lon, my_packet.lon_hemis
	print "latitude:\t", my_packet.lat, my_packet.lat_hemis
	print "time stamp:\t", my_packet.t_hours,":",my_packet.t_mins,":",my_packet.t_secs,"\n"

