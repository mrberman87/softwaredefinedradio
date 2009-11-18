#!/usr/bin/env python

#############################################################################
#Queue class for handling ground queue before sending data to be packetized.#
#The queue has no maximum, it will have to be handled by the gui unless     #
#            otherwise asked.                                               #
#def add   	: always appends to the end of the list		            #
#def delete	: deletes the index specified, index starts at 0            #
#def order 	: removes the item from the queue at move_from and inserts  #
#	     	  pushing everything at and after move_to to the right one  #
#		  index.						    #
#def size  	: returns the length of the current queue                   #
#def return_head: deletes and returns the first item in the list.           #
#############################################################################

class queue():
	
	def __init__(self):
		self.queue_store = []
		self.temp = ''

	def add(self, new_item):
		self.queue_store.append(new_item)

	def delete(self, index):
		self.queue_store.pop(index)

	def order(self, move_from, move_to):
		self.temp = self.queue_store.pop(move_from)
		self.queue_store.insert(move_to, temp)
		self.temp = ''

	def print_q(self):
		print self.queue_store

	def return_head(self):
		return self.queue_store.pop(0)

	def size(self):
		return len(self.queue_store)
