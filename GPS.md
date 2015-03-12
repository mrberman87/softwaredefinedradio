# Testing without a GPS module #
gpsd is available through the synaptic package manager, so there's no need to compile from source.
To test gpsd:
  1. make sure you have the **python-gps** and **gpsd-clients** installed.
  1. use gpsfake to fool gpsd into thinking you have a GPS device attached that is spitting out data. To do this run the following command:('input.txt' is a file of your choice with NMEA strings.)
```
$ gpsfake input.txt
```
  1. Open another terminal window and run the one of the GUI tools that let's you view the telemetry data by typing:
```
$ xgps
```
  1. You should see data in the window if everything is set up correctly. If so, you can now test your own gps program. One option is to make queries via telnet. Since you are more than likely using the computer that the 'fake gps' is connected to, run the following command:
```
 $ telnet localhost 2947
```
2947 is the default port, and localhost is your loopback address. In most cases, you will not need to change this.
# Troubleshooting #

### Unable to telnet into localhost. Cannot ping localhost ###
Theres a good chance that your loopback device was not enabled at startup. To check type:
```
$ ifconfig
```
If there is no lo device, this is your problem. Fix it by typing
```
$ sudo ifconfig lo up
```

### Garmin Serial GPS18 appears to be unreponsive under gpsd ###
First, check to see if the device is presenting any type of data. Type:
```
$ cat /dev/ttyS0
```
The digit following ttyS will vary, depending on which serial port is being used.

If no text appears, then the problem is most likely with the GPS device.

If there are incomprehensbile symbols showing up, then verify whether the buad rate is correct.

**GPS18 LVC oddity** - The [Garmin Technical Specifications](http://www8.garmin.com/manuals/425_TechnicalSpecification.pdf) documentation for this module states that the factory default is the NMEA standard baud rate of 4800. The default seems to be 19200.
If there is readable text, the problem is probably not with the GPS device. Verify whether gpsd is listening to the correct serial device.




# Links #

[gpsd homepage](http://gpsd.berlios.de/) - service daemon that can interface with a GPS device and make the data available to be queried on a TCP port.

[Garmin GPS 18 LVC](http://www8.garmin.com/manuals/425_TechnicalSpecification.pdf) - documenation for GPS device currently being used.

[PCM-3292 resources](http://www.emacinc.com/manuals_drivers.htm) - Site with drivers and documentation for the PCM3292 GPS device that is no longer being used.