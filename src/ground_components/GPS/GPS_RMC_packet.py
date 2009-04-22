#Derrick Jones
#Class represents: RMC-Recommended Minimum Specific GNSS Data
#This sentence comes in the form:
#$GPRMC,hhmmss.dd,S,xxmm.dddd,<N|S>,yyymm.dddd,<E|W>,s.s,h.h,ddmmyy,d.d,<E|W>,M*hh<CR><LF>

class GPS_RMC_packet:
	t_hours=None
	t_mins=None
	t_secs=None
	status=None
	lat=None
	lat_hemis=None
	lon=None
	long_hemis=None
	speed_knots=None
	heading=None
	full_date=None
	declination=None
	mode=None
	altitude=None	
	'''#altitude is not including in the RMC string. This packet includes an altitude attribute
	 to prevent crashes in the event that another class tries to access it.'''
	
	def __init__(self, input_string):
		#parse the comma delimited NMEA string into an array
		gps_data_array=input_string.split(',')
		try:
			t_string=gps_data_array[1]
			self.t_hours=t_string[:2]
			self.t_mins=t_string[2:4]
			self.t_secs=t_string[4:]
			self.status=gps_data_array[2] #A=valid, V=invalid
			self.lat=gps_data_array[3]
			self.lat_hemis=gps_data_array[4]
			self.lon=gps_data_array[5]
			self.long_hemis=gps_data_array[6]
			self.speed_knots=gps_data_array[7]
			self.heading=gps_data_array[8]
			self.full_date=gps_data_array[9]
			self.declination=gps_data_array[10] #East or west
			self.mode=gps_data_array[11]
		except:
			print "invalid NMEA string:",input_string
		
		
