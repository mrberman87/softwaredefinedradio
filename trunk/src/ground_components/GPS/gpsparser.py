'''
Created on Mar 29, 2009

@author: derrick
'''
from GPS_GGA_packet import GPS_GGA_packet
from GPS_RMC_packet import GPS_RMC_packet
from time import strftime,gmtime
class gpsparser:
	current_packet=None
	previous_packet=None
	log_file_name="log.txt"                     #default filename for log
	log_file=None
	
	def __init__(self,log_file_name):
		pass

	def update_packet(self,gpsd_string):
		#accepts a string from gpsd. Only expects one type of string.
		pass
			
	def update_log(self,message):
		#time stamps the given message and writes it at the end of the object's log file
		time_stamp=strftime("%d %b %Y %H:%M:%S\t", gmtime())
		self.log_file.write(time_stamp+message)
