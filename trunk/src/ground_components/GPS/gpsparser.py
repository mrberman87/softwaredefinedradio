############################################################################
#GPS packet object to be used by ground station GUI to display GPS data.
############################################################################
from GPS_packet import GPS_packet
from time import strftime,gmtime
class gpsparser:
	current_packet=None
	previous_packet=None                     #default filename for log
	log_file=None
	
	def __init__(self, name = "log.txt",write_opt = 'a'):
			self.log_file = open(name, write_opt)
			self.update_log("logging started")

	def update_packet(self,gpsd_string):
		#accepts a string from gpsd. Only expects one type of string
		self.current_packet = GPS_packet(gpsd_string)

	def update_log(self,message):
		#time stamps the given message and writes it at the end of the object's log file
		time_stamp=strftime("%d %b %Y %H:%M:%S\t", gmtime())
		self.log_file.write(time_stamp+message)
