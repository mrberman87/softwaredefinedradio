'''
Created on Mar 29, 2009

@author: derrick
'''
from GPS_RMC_packet import GPS_RMC_packet
from GPS_GGA_packet import GPS_GGA_packet
class gpsparser:
    current_packet=None
    previous_packet=None
    log_file_name="log.txt"                     #defualt filename for log
    log_file=None
    
    def __init__(self,log_file_name):
        try:
            log_file=open(log_file_name,'a')
        except IOError:
            pass
    def update_packet(self,nmea_string):
        nmea_array=nmas_string.split(',')
        previous_packet=current_packet  #save the current packet in case the new packet is invalid
        if nmea_array[0] == '$GPRMC':
            current_packet=GPS_RMC_packet(nmea_string)
        elif nmea_array[0] == '$GPGGA':
            current_packet=GPS_GGA_packet(nmea_string)
        else:
            pass    #insert real statement when we figure out how to handle invalid strings
        
