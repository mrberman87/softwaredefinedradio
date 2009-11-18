#!/usr/bin/python

"""model_tester.py used to test functionality of ground_components without
the need for a GUI"""
import ground_controls

m = ground_controls.ground_controls()
m.start() #start the command processing thread
#test list is a list of commands to add to the queue
#testlist=["GPS", "Image", "Batt", "Freq TX: 440e6+100e3 RX: 440e6-50e3"]
testlist=["GPS"]
for req in testlist:
	try:
		m.addToQueue(req)
	except ground_controls.QueueLimitException:
		print "max queue exceeded!"
		continue
