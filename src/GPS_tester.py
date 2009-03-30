#!/usr/bin/env python
'''
Derrick Jones
UAV Software Defined Radio
Simple test driver for GPS_GGA_packet class
'''

from GPS_GGA_packet import GPS_GGA_packet


my_file=open('gps_strings.txt','r');  #open file for reading
my_line_queue=list()    
for line in my_file.readlines():
    my_line_queue.append(line)
    
my_file.close();    #close file handle so other proceses can access it

for item in my_line_queue:
    my_packet=GPS_GGA_packet(item);
    print "altitude:\t", my_packet.altitude,'m'
    print "longitude:\t", my_packet.long, my_packet.long_hemis
    print "latitude:\t", my_packet.lat, my_packet.lat_hemis
    print "time stamp:\t", my_packet.t_hours,":",my_packet.t_mins,":",my_packet.t_secs
    
