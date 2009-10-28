#!/usr/bin/env python

import os, ctypes, usb, time, subprocess
from daemon import *
from txrx_controller import *
from GPS_getter import *
from wd_reset import *

class uav_controller():
        def run(self):
                #set priority
                os.system("renice 0 %d" % os.getpid())
                #changing the system name of this program when it's running
                libc = ctypes.CDLL('libc.so.6')
                libc.prctl(15, 'UAV Controller', 0, 0, 0)
                self.log("Starting Up: pid = %d" % os.getpid())
                #setting up the usb controller
                self.dev = usb.core.find(idVendor=65534, idProduct=2)
                self.dev.set_configuration()
                #starting threads to reset the watchdog timers
                self.wd1 = wd_reset('/uav/daemon_pids/wd1_controller.wd', 5).start()
                self.wd2 = wd_reset('/uav/daemon_pids/wd2_controller.wd', 5).start()
                #intializing the system
                self.init_vars()
                self.init_files()
                #self.check_saved_vars()
                #set_params will initialize self.trans, it is just being allocated here
                self.trans = None
                #the next line is to set the link to d8psk outright for testing
                self.version = '8psk'
                self.set_params()
                self.gps = GPS_getter()
               
                #initialize local variables specific to controlling the transceiver
                rx = True
                tx = True
                going_home = False
               
                #This is the main controller section of code
                while True:
                        #this condition deals with receiving things from the ground
                        if rx:
                                tmp = self.trans.receive()
                                #this is reached when a transmission is completed normally, and the other
                                #side gets all of the data
                                if tmp is True or tmp == 'Transmission Complete':
                                        tx = self.exec_command(self.get_command())
					self.clear_file(self.f_name_rx)
                                        self.errors = 0
                                #this is reached when there is an error and either a timeout is reached, or
                                #the transmission cannot complete with the given number of hand shakes
                                elif tmp == 'Handshaking Maximum Reached' or tmp == 'Timeout':
                                        self.send_error(tmp)
                                        tx = True
                                        self.errors = self.errors + 1
                                #this is reached when there is a general error from the ground
                                elif tmp == 'Error':
                                        tx = True
                                        self.errors = self.errors + 1
                       
                        #this condition deals with getting errors with receiving
                        if self.errors > 3:
                                self.log("Had more than 3 errors, going home!")
                                self.send_error("going home")
                                going_home = True
                                self.errors = 0
                       
                        #this condition deals with transmitting data back to the ground
                        if tx:
                                tmp = self.trans.transmit(self.f_name_tx)
                                #this section is reached when the transmission completes as normal
                                if tmp is True or tmp == 'Transmission Complete':
                                        rx = True
                                        self.errors = 0
                                        #this handles the "go home" situation due to too many errors
                                        if going_home:
                                                self.go_home()
                                                self.set_params()
                                                going_home = False
                                #this section is reached when there is a problem sending the information to the other
                                #side of the link
                                elif tmp == 'Handshaking Maximum Reached' or tmp == 'Timeout' or tmp == 'Error':
                                        rx = False
       
        #this method sets up the transmittion of an erroneous message
        def send_error(self, msg):
                self.f_name_tx = '/misc.dat'
                path = self.working_dir + self.f_name_tx
                self.clear_file(path)
                fd = open(path, 'w')
                fd.write(msg)
                fd.close()
       
        #this method takes the command from the ground, and executes what it needs to in order to fulfill the command
        def exec_command(self, command):
                #this changes the communication link's settings (ie - frequency, modulation scheme, etc.)
                if(command == "Settings"):
                        log = "Changing Settings:"
                        fd = open(self.working_dir + self.f_name_rx, 'r')
                        #this for loop goes through the file and pulls out only what is sent to be changed
                        for l in fd:
                                if l.startswith("Freq:"):
                                        junk, tmp_freq = l.split()
                                        if tmp_freq != None:
                                                self.freq = int(tmp_freq)
                                                log = log + " Freq = %d" % self.freq
                                if l.startswith("Timeout:"):
                                        junk, tmp_time_0 = l.split()
                                        if tmp_time_0 != None:
                                                self.time_0 = int(tmp_time_0)
                                                log = log + " Timeout = %d" % self.time_0
                                if l.startswith("Hand_Max:")
                                        junk, tmp_hand_max = l.split()
                                        if tmp_hand_max != None:
                                                self.hand_max = int(tmp_hand_max)
                                                log = log + " Handshaking Max = %d" % self.hand_max
                                if l.startswith("Version:"):
                                        junk, tmp_version = l.split()
                                        if tmp_version != None:
                                                self.version = tmp_version
                                                log = log + " Modulation Scheme = %s" % self.version
                        fd.close()
                       
                        #this deals with a modulation scheme change
                        if tmp_version != None:
                                self.set_params()
                        #this deals with the change of any other variable
                        else:
                                if tmp_freq != None:
                                        self.trans.set_frequency(self.freq)
                                if tmp_time_0 != None:
                                        self.trans.set_frame_time_out(self.time_0)
                                if tmp_hand_max != None:
                                        self.trans.set_hand_shaking_maximum(self.hand_max)
                        self.log(log)
                        return False
                #this takes a picture
                elif(command == "Image"):
                        self.log("Taking Picture")
                        self.f_name_tx = "/pic.jpg"
                        self.pic = subprocess.Popen('uvccapture -q100 -o%s' % (self.working_dir + self.f_name_tx), shell=True)
                        while self.pic.poll != None:
                                if time.time() - time_not > 5:
                                        self.f_name_tx = "Error"
                                        self.kill_pid(self.pic.pid)
                                        break
                        time.sleep(2)
                        return True
                #this gets an FFT of the air
                elif(command == "FFT"):
                        self.log("Getting FFT Data")
                        del self.trans
                        self.dev.reset()
                        time.sleep(2)
                        self.f_name_tx = "/fft_image.jpeg"
                        time_not = time.time()
                        self.fft = subprocess.Popen('python get_fft.py %s/RC.dat, %s' % (self.working_dir, self.working_dir + self.f_name_tx), shell=True)
                        while self.fft.poll != None:
                                if time.time() - time_not > 10:
                                        self.f_name_tx = "Error"
                                        self.kill_pid(self.fft.pid)
                                        break
                        self.set_params()
                        return True
                #this gets temprature and battery voltage as well as GPS location of the UAV
                elif(command == "Telemetry"):
                        self.log("Getting Telemetry Data")
                        self.tel = subprocess.Popen('python telemetry.py', shell=True)
`                       self.f_name_tx = "/misc.dat"
                        while self.tel.poll != None:
                                if time.time() - time_not > 5:
                                        self.f_name_tx = "Error"
                                        self.kill_pid(self.tel.pid)
                                        break
                        return True
                elif(command == "GPS"):
                        self.log("Getting GPS Data")
                        self.f_name_tx = "/misc.dat"
                        self.gps.get_gps('w', self.working_dir + self.f_name_tx)
                        return True
                #this will execute a cli command, and send the result back to the gound
                elif(command == "command"):
                        fd = open(self.working_dir + self.f_name_rx, 'r')
			cli = fd.readline()  #the command is on the second line
                        cli = fd.readline().strip('\n').strip()
                        fd.close()
                        self.log("Executing Command: %s" % cli)
                        self.f_name_tx = "/misc.dat"
                        self.comm = subprocess.Popen('%s > %S' % (cli, self.working_dir + self.f_name_tx), shell=True)
                        self.comm.wait()
                        return True
       
        #this parses out what the command to be executed from the ground is
        def get_command(self):
                fd = open(self.f_name_rx, 'r')
                tmp = fd.readline().strip('\n').strip()
                fd.close()
                return tmp
       
        #this appends a log file with useful, timestamped information
        def log(self, string):
                fd = open("log.dat", "a")
                fd.write(str(time.ctime(time.time())) + "     " + string + '\n')
                fd.close()
       
        #this clears the contents of a given file
        def clear_file(self, path):
                p = subprocess.Popen('>%s' % path, shell=True)
                p.wait()
       
        #this checks if a given pid exists on the system
        #if it is a zombie, it will kill it
        def pid_exists(self, pid):
                try:
                        fd = open('/proc/%d/status' % pid, 'r')
                        for l in fd:
                                if(l.startswith('State:')):
                                        junk, s, text = l.split( None, 2 )
                        fd.close()
                        if(s != "Z"):
                                return True
                        os.waitpid(pid, os.WNOHANG)
                        return False
                except IOError, OSError:
                        return False
       
        #this kills any process given its pid
        def kill_pid(self, pid):
                try:
                        os.kill(pid, 9)
                        return not self.pid_exists(pid)
                except OSError:
                        return True
       
        #this initializes class level variables
        def init_vars(self):
                self.go_home()
               
                #file name of what is going to be sent to the ground
                self.f_name_tx = ''
               
                #file name of what has been sent to the air
                self.f_name_rx = '/rx_data'
               
                #this tracks the number of erroneous tries on the data link before going home
                self.errors = 0
               
                #sets where the working direcotry is even if os.getcwd() is not here
                self.working_dir = '/uav'
       
        #this sets the "go home" variables
        def go_home(self):
                self.freq = 440000000
                self.rx_offset = -50e3
                self.tx_offset = 100e3
                self.time_0 = 35
                self.hand_max = 5
                self.version = 'bpsk'
       
        #this sets parameters for the txrx_controller
        #calling this will also initialze the controller
        def set_params(self):
                del self.trans
                self.dev.reset()
                time.sleep(2)
                self.trans = txrx_controller(hand_shaking_max = self.hand_max, frame_time_out = self.time_0,
                        work_directory=self.working_dir, version = self.version, fc = self.freq, centoff=0,
                        foffset_tx=100e3, foffset_rx=-50e3, rx_file=self.f_name_rx)
                time.sleep(2)
       
        #this initializes files that the UAV controller may need in its operation
        def init_files(self):
                #This method makes sure that all files needed for this
                #program are exist.
                if(not os.path.exists("pic.jpg")):
                        subprocess.Popen('touch fft_image.jpeg', shell=True)
                if(not os.path.exists("fft_image.jpeg")):
                        subprocess.Popen('touch sensor.dat', shell=True)
                if(not os.path.exists("misc.dat")):
                        subprocess.Popen('touch misc.dat', shell=True)
                if(not os.path.exists("gps.dat")):
                        subprocess.Popen('touch gps.dat', shell=True)
                if(not os.path.exists("log.dat")):
                        subprocess.Popen('touch log.dat', shell=True)
                if(not os.path.exists("RC.dat")):
                        subprocess.Popen('touch RC.dat', shell=True)
                if(not os.path.exists("rx_data")):
                        subprocess.Popen('touch rx_data', shell=True)
       
        #this loads up variables that were saved from the previous run of this process
        def check_saved_vars(self):
                path = self.working_dir + '/saved_vars'
                if not os.path.exists(path):
                        return
                fd = open(path, 'r')
                self.freq = int(fd.readline().strip('\n').strip())
                self.version = fd.readline().strip('\n').strip()
                fd.close()
                os.remove(path)
                return
       
        #this handles the book keeping of processes, and saving variables
        def __del__(self):
                self.log("Closeing")
                if self.pid_exists(self.pic.pid):
                        self.kill_pid(self.pic.pid)
                if self.pid_exists(self.fft.pid):
                        self.kill_pid(self.fft.pid)
                if self.pid_exists(self.tel.pid):
                        self.kill_pid(self.tel.pid)
                if self.pid_exists(self.merg.pid):
                        self.kill_pid(self.merg.pid)
                if self.pid_exists(self.comm.pid):
                        self.kill_pid(self.comm.pid)
               
                """path = self.working_dir + '/saved_vars'
                p = subprocess.Popen('touch %s' % path, shell=True)
                os.waitpid(p.pid, 0)
                fd = open(path, 'w')
                fd.write("%d\n" % self.freq)
                fd.write("%s\n" % self.version)
                fd.close()"""


if __name__ == '__main__':
        uav_controller().run()
        """
        #this sets up this controller as a daemon to run in the background
        daemon = uav_controller('/uav/daemon_pids/uav_controller.pid')
        if len(sys.argv) == 2:
                if 'start' == sys.argv[1]:
                        daemon.start()
                elif 'stop' == sys.argv[1]:
                        daemon.stop()
                elif 'restart' == sys.argv[1]:
                        daemon.restart()
                else:
                        print "Unknown command"
                        sys.exit(2)
                sys.exit(0)
        else:
                print "usage: %s start|stop|restart" % sys.argv[0]
                sys.exit(2)"""
