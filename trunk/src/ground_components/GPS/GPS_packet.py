#!/usr/bin/env python
############################################################################
############################################################################
class GPS_packet:
	t_hours = None
	t_mins = None
	t_secs = None
	lat = 0
	lat_hemis = None
	lon_hemis = None
	lon = 0
	sog = 0		#speed over ground
	alt = 0

	def __init__(self, input_string):
			#expects a string based on gpsd repsonse given 'pave' single
			# letter commands
			gps = input_string.split(',')
			pos_str = gps[1]	#position(lat and lon) "$P=lat lon"
			alt_str = gps[2]	#altitude
			sog_str = gps[3]	#speed over ground
			err_str = gps[4]	#estimated error string

			#Position
			pos = pos_str.split(' ') #split by spaces
			#latitude is first
			lat = pos[0][2:] #skip the 'P='
			lon = pos[1]
			
			self.lat = abs(float(lat))	#don't want negative signs
			self.lat_hemis = ('W' if self.lat == lat else 'E')

			self.lon = abs(float(lon))	#don't want negative signs
			self.lon_hemis = ('N' if self.lon == lon else 'S')

			self.sog = sog_str
			self.alt = alt_str
