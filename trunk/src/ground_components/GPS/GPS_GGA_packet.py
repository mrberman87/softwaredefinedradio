#Derrick Jones
#Class represents: GGA - Global Positioning System Fix Data
#Time, position and fix related data for a GPS reciever.

#This NMEA sentence comes in the form:
#$GPGGA,hhmmss.dd,xxmm.dddd,<N|S>,yyymm.dddd,<E|W>,v,ss,d.d,h.h,M,g.g,M,a.a,xxxx*hh<CR><LF>


class GPS_GGA_packet:
	t_hours=0
	t_mins=0
	t_secs=0
	lat=0
	lat_hemis=None
	lon=0
	long_hemis=None
	valid_fix=0
	num_of_sats=0
	hdop=0
	altitude=0
	wgs84_diff=0
	
	def __init__(self, input_string):
		#Parse comma delimited input string
		gps_data_array=input_string.split(',')
		try:	#assign values to class attributes in a usable format
			#UTC TIme
			t_string=gps_data_array[1]
			#split the time string up by character
			self.t_hours=t_string[0:2]	
			self.t_mins=t_string[2:4]	
			self.t_secs=t_string[4:]	#string indices 4 to last item
		
			#Latitiude
			self.lat=gps_data_array[2]
			self.lat_hemis=gps_data_array[3]		#(N or S for North/South)
			
			#Longitude
			self.lon=gps_data_array[4]
			self.long_hemis=gps_data_array[5]		#E or W for East or West
			
			#-----Other info--------------------------
			self.valid_fix=gps_data_array[6]		#1 if valid, 0 if not
			self.num_of_sats=int(gps_data_array[7])	#number of satellites used in position fix (ss)
			self.hdop=gps_data_array[8]				#Horizontal Dilution of Position (d.d)
			self.altitude=gps_data_array[9]		#mean sea level(h.h)
			self.wgs84_diff=gps_data_array[10]	#difference between WGS-84 reference ellipsoid surface and mean sea level alt
		except:
			print "invalid NMEA string: ", input_string


	
	
