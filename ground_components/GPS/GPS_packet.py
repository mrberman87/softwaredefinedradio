#!/usr/bin/env python
############################################################################
'''
The Data structure is to be used by a gpsparser object. the init method
takes response strings from gpsd to populate the members of the structure.
Members can be used to populate the fields in the GUI.
'''
############################################################################
from time import strftime,gmtime
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
				'''
				IndexError exception should only occur if there are is
				no ' ' in the position field. Usually means we got a
				'P=?' for a string.
				'''
				self.write_parse_error()
				lat = 0
				lon = 0

			try:
				self.lat = abs(float(lat))	#don't want negative signs
				lat_hemis = ('S' if self.lat == lat else 'N')
				self.lat = str(self.lat) + " " + lat_hemis

				self.lon = abs(float(lon))	#don't want negative signs
				lon_hemis = ('E' if self.lon == lon else 'W')
				self.lon = str(self.lon) + " " + lon_hemis
			except TypeError:
				self.write_parse_error()

			self.sog = sog_str[2:]
			self.alt = alt_str[2:] + " m" #meters above sea level

	def write_parse_error(self):
		time_stamp=strftime("%d %b %Y %H:%M:%S\t", gmtime())
		sys.stderr.write(time_stamp + "error: lat and lon not available\n")
