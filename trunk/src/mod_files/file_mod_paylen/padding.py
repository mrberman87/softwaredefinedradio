#!/usr/bin/env python

"""
This program's intention is to make the file that is being sent modulo the
payload length such that the USRP will send all packets and not miss the 
last one due to it not filling out the minimum size requirements of the
payload for a packet.
"""

payload_length = 1024

#Open and read the data origination file for padding operations
not_padded = open("/home/sab/Desktop/unpadded.py", "r")
original_data = not_padded.read()
not_padded.close()

"""
Determine amount of padding so that the first line includes the original
file length along with enough white space to create an entire packet 
including the new line character. If this original data is pad 
sensitive like an image, then the new line character goes with the first 
packet and the original data has no new line character to begin with
when re-written at the recieve end.
"""
padded_first_line = str(len(original_data)) + (payload_length - 2 - len(str(len(original_data))))*' ' + '\n'
end_file_pad = ((len(padded_first_line + original_data)/payload_length + 1)*payload_length - len(padded_first_line + original_data))*' '

#Write all pads and original data to new file to be sent
padded = open("/home/sab/Desktop/padded.py", "w")
padded.write(padded_first_line + original_data + end_file_pad)
padded.close()
