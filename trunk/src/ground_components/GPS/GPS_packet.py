#!/usr/bin/env python
############################################################################
############################################################################
import sys

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
			try:
				lon = pos[1]
			except IndexError:
				sys.stderr.write("lat and lon not available")
				lat = None
				lon = None

			try:
				self.lat = abs(float(lat))	#don't want negative signs
				self.lat_hemis = ('S' if self.lat == lat else 'N')

				self.lon = abs(float(lon))	#don't want negative signs
				self.lon_hemis = ('E' if self.lon == lon else 'W')
			except TypeError:
				sys.stderr.write("lat and lon not available")

			self.sog = sog_str[2:]
			self.alt = alt_str[2:]
