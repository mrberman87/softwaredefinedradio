#!/usr/bin/env python
#  						RS232 PIN ASSIGNMENT FOR DB-9                                      
#                         ****************************       PIN:1..........CD			PIN:6..........DSR			
#                          **1 ** 2  ** 3 ** 4 ** 5**        PIN:2..........RD 			PIN:7..........RTS
#		            ************************         PIN:3..........TD			PIN:8..........CTS
#                             * 6 **  7 ** 8 ** 9 *          PIN:4..........DTR			PIN:9..........RING IND.
#                              ******************            PIN:5......... SIG GND
#

import timeit, time, serial, sys, os
#The Power function is the element in which the imported module "time" will time. In this case test is the time that 
#the CTS line is low.
#open serial port zero, Trigger the circuit,loop while control line is high,pass is just a place holder, close serial port 
def Power():
 	s = serial.Serial(0)
	trigger(s) 
	#Pin number 6
	while(not s.getDSR()):
		pass
	s.close()
# trigger(s) is a function that triggers the circuit with a momentarily active low pulse.
#This active low Pulse is required by the hardware of the circuit. Specificly the 555(6) timer.
#You may notice that the Active low in the software, is not actually low. This is because of the hardware(MAX 232) that converts the 
#the data from TTL--->serial and from serial--->TTL. Because of this a TTL low pulse (0 V) is serial(+12V) and TTL HIGH or 5V is serial (-12 ).
#so if  the function, push_low sends a 1(+12Vserial) this will be a TTL(0V) which is the active low which we want to trigger the circuit
def trigger(s):
	s.setDTR(1)
	time.sleep(.001)
	s.setDTR(0)

def decode_data(value):
	Batt=-19.005*value + 43.823
	#Batt=-21.189*value*value*value+103.33*value*value-184.69*value+131.42
	print "%.1f Volts" % Batt 
	return Batt
if __name__ == '__main__':
	t=timeit.Timer('Power()', "from __main__ import Power")
	#while(True):
	batt=decode_data(t.timeit(number=1))
	#time.sleep(1)
#-----------------------------------------------------------------------------------------------
#Output to file for circuit curve fitting (used only to get equation)
	fd = open(os.getcwd() + '/misc.dat', 'a')
	fd.write("%.1f\n" % (batt))
	fd.close()		
		

