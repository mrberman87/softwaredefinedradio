How to use the txrx_controller.py

import txrx_controller
tb = txrx_controller.txrx_controller()

*To transmit a new Frame:
	
	tb.transmit( DATA )

	DATA can be a passed variable or a file location inside /softwaredefinedradio/src
	Need to always have / in the beginning of the user input path so the controller will
	recognize you are passing a file that needs to be opened. The path is also set in a
	variable and needs to be updated for each login it is used on.

*To receive

	tb.receive()

	This will return something when it is done. If you are receiving a new frame, then it will
	return the data that was received in a file. If you transmitted a new frame and are awaiting
	confirmation that the handshaking is complete, then once that occurs it will return True.



How to use tx_rx_path.py

import tx_rx_path

What tb is:

	tb = tx_rx_path.tx_rx_path()

Start:
	
	tb.Start()

		Begins the script for transmission and reception

Stop:

	tb.Stop()
		
		Stops the script closes the device out

To put data into the transmit path:

	tb.msg_queue_in.insert_tail(gr.message_from_string( DATA ))

To retrieve data that is received:

	tb.msg_queue_out.delete_head_nowait().to_string()

		If nothing is in the queue it will throw an error, will most likely have to put in a try block.

To check if the receive queue is empty:

	tb.msg_queue_out.empty_p()

		Will return True if the queue is empty and False if it has at least 1 item present.

To tell the transmit queue no more data is coming:

	tb.msg_queue_in.insert_tail(gr.message(1))
		
		This is for exiting gracefully.

The transmit path must have full packets dropped into the message source queue.
The receive path will generate payloads that will be dropped in the message sink queue.
