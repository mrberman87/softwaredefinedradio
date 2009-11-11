#!/usr/bin/env python
#  						RS232 PIN ASSIGNMENT FOR DB-9                                      
#                         ****************************       PIN:1..........CD			PIN:6..........DSR			
#                          **1 ** 2  ** 3 ** 4 ** 5**        PIN:2..........RD 			PIN:7..........RTS
#		            ************************         PIN:3..........TD			PIN:8..........CTS
#                             * 6 **  7 ** 8 ** 9 *          PIN:4..........DTR			PIN:9..........RING IND.
#                              ******************            PIN:5......... SIG GND
#

import timeit, time, serial, sys
#------------------------------------------------------------------------------------------------
#The Temp function is the element in which the imported module "time" will time. In this case test is the time that 
#the CTS line is low.
#open serial port zero, Trigger the circuit,loop while control line is high,pass is just a place holder, close serial port 

def Temp():
	s = serial.Serial(0)
	push_low(s)
	while(not s.getCTS()):
 		pass
	s.close()
	
#-----------------------------------------------------------------------------------------------
#The Power function is the element in which the imported module "time" will time. In this case test is the time that 
#the CTS line is low.
#open serial port zero, Trigger the circuit,loop while control line is high,pass is just a place holder, close serial port 

def Power():
 	s = serial.Serial(0)
	trigger_2(s) 
	#Pin number 6
	while(not s.getDSR()):
		pass
	s.close()
	
#--------------------------------------------------------------------------------------------
# Push_low is a function that triggers the circuit with a momentarily actective low pulse.
#This active low Pulse is required by the hardware of the circuit. Specificly the 555(6) timer.
#You may notice that the Active low in the software, is not actually low. This is because of the hardware(MAX 232) that converts the 
#the data from TTL--->serial and from serial--->TTL. Because of this a TTL low pulse (0 V) is serial(+12V) and TTL HIGH or 5V is serial (-12 ).
#so if  the function, push_low sends a 1(+12Vserial) this will be a TTL(0V) which is the active low we want to trigger the circuit 
def push_low(s):
	s.setRTS(1)
	time.sleep(.001)
	s.setRTS(0)
	

def trigger_2(s):
	s.setDTR(1)
	time.sleep(.001)
	s.setDTR(0)
	
#----------------------------------------------------------------------------------------------
# The decode defenition is an equation derived from the temp file during testing. Tempurature values  of 0 to 300 degrees F "Voltages" were
# simulated using voltages from 0-3.0V by increments of 0.1 Volts. The data was mapped to excel and the equation below was dervived. The
# value is actually the unique pulse width for a given Tempurature. 
def decode_data(value1):
	Tempurature = 549.69*value1*value1 - 1194.4*value1 + 439.13
	print "%d F" % Tempurature
	return Tempurature
	
def decode_data2(value2):
	Batt=-58.743*value2+26.115
	print "%.1f Volts" % Batt 
	print '\n'
	return Batt

from optparse import OptionParser
#----------------------------------------------------------------------------------------------

if __name__ == '__main__':
	#tmp = sys.argv[1]
	#if tmp.tolower() == 'test':
	t=timeit.Timer('Temp()', "from __main__ import Temp")
	t2=timeit.Timer('Power()', "from __main__ import Power")
	#while(True):
	temp = decode_data(t.timeit(number=1))
	batt = decode_data2(t2.timeit(number=1))
	#time.sleep(1)
		
		
#-----------------------------------------------------------------------------------------------
#Output to file for circuit curve fitting (used only to get equation)
	fd = open('/uav/misc.dat', 'w')
	fd.write("%d\n%d" % (temp, batt))
	


