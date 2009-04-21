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
	log_file_name="log.txt"                     #defualt filename for log
	log_file=None
	
	def __init__(self,log_file_name):
		try:
			self.log_file=open(log_file_name,'a')
			self.log_file.write("\n")
		except IOError:
			'''will more than likely add a prompt to ask user to try again. Will depend on
			GUI integration'''
			pass

	def update_packet(self,nmea_string):
		self.update_log(nmea_string)	#write input of parser to the specified log file
		self.nmea_array=nmea_string.split(',')
		self.previous_packet=self.current_packet #save the current packet in case the new packet is invalid
		if self.nmea_array[0] == '$GPRMC':
			self.current_packet=GPS_RMC_packet(nmea_string)
		elif self.nmea_array[0] == '$GPGGA':
			self.current_packet=GPS_GGA_packet(nmea_string)
		else:
			#will silently restore the previous packet if given a string that is not RMC or GGA format
			self.current_packet=self.previous_packet
			
	def update_log(self,message):
		#time stamps the given message and writes it at the end of the object's log file
		time_stamp=strftime("%d %b %Y %H:%M:%S\t", gmtime())
		self.log_file.write(time_stamp+message)