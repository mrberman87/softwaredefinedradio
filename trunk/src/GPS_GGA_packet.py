#Derrick Jones
#Class represents: GGA - Global Positioning System Fix Data
#Time, position and fix related data for a GPS reciever.

#This NMEA sentence comes in the form:
#$GPGGA,hhmmss.dd,xxmm.dddd,<N|S>,yyymm.dddd,<E|W>,v,ss,d.d,h.h,M,g.g,M,a.a,xxxx*hh<CR><LF>
class GPS_GGA_packet:
	t_hours=0
	t_mins=0
	t_secs=0
	latitude=0
	lat_hemis=None
	longitude=0
	lon_hemis=None
	valid_fix=0
	num_of_sats=0
	hdop=0
	altitude=0
	wgs84_diff=0
	
	def __init__(self, input_string):
		#----------------------------------------------------------------------------------------------------------------------------------------------
		#Separate comma delimited input string
		#----------------------------------------------------------------------------------------------------------------------------------------------
		gps_data_array=input_string.split(',') 
		if(len(gps_data_array)<11):
		  valid_fix=False
		  i=len(gps_data_array)-1
		  while i < 11:
		  	data_array.append(0)
		  	
		  	
		time=float(gps_data_array[1])
		latitude=float(gps_data_array[2])
		lat_hemisphere=gps_data_array[3]
		longitude=float(gps_data_array[4])
		long_hemisphere=gps_data_array[5]
		valid_fix=gps_data_array[6]
		num_of_sats=int(gps_data_array[7])
		hdop=gps_data_array[8]
		altitude=gps_data_array[9]
		wgs84_diff=gps_data_array[10]
		
		#-----------------------------------------------------------------------------------------------------------------------------------------------
		#assign values to class attributes in a usable format
		#------------------------------------------------------------------------------------------------------------------------------------------------
		#UTC TIme
		self.t_hours=int(time)/10000
		self.t_mins=(int(time)%10000)/100
		self.t_secs=int(time%100)
		
		
		#Latitiude
		self.latitude=latitude
		self.lat_hemis=lat_hemisphere		#latitudinal hemisphere (N or S for North/South)
		
		#Longitude
		self.longitude=longitude
		self.lon_hemis=long_hemisphere		#E or W for East or West
		
		#-----Other info--------------------------
		self.valid_fix=valid_fix		#1 if valid, 0 if not
		self.num_of_sats=num_of_sats	#number of satellites used in position fix (ss)
		self.hdop=hdop			#Horizontal Dilution of Position (d.d)
		self.altitude=altitude		#mean sea level(h.h)
		self.wgs84_diff=wgs84_diff	#difference between WGS-84 reference ellipsoid surface and mean sea level alt
	
	
