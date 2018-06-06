###################################################################################################################
# File: serialports.py
# Course: 17640
# Project: IoT Order Fulfillment Center
# Copyright: Copyright (c) 2018 Carnegie Mellon University (ajl)
# Versions:
#   1.0 April 2018 - Initial write (ajl).
#
# Description: This class serves as an example for how to write an application that determine what serial ports
# are available on the PC/Mac. This could be used as a basis to create a more comprehensive application to 
# communicate with the orderfulfillment robots.
#
# Parameters: None
#
# Internal Methods:
#  None
#
# External Dependencies:
#   - python 2.7
#   - sys
#   - glob
#   - serial ## pyserial-3.2.1 library
###################################################################################################################

import sys
import glob
import serial 

# Here we try to figure out which kind of machine we are on Winows, linux, or mac.
# Once we determine which machine, we create a list of available ports.
def get_port():
    port_return = []
    if sys.platform.startswith('win'):
        # Windows
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # Linux - this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        # Mac OS   
        ports = glob.glob('/dev/tty.*')
    else:
        # No idea
        print('Unsupported platform')
    #print ('================= Available Ports ==================\n')

    # Here we print each port that we found to the terminal.

    for i in range(0, len(ports)):

        #print ('====================================================\n')
        
        try: 
            ser = serial.Serial(ports[i])
            #print ('Port name:: ' + ports[i] + '\n')
            #print (ser)
            #print ('\n')
            ser.close()
            port_return.append(ports[i])
        except serial.SerialException:
            #print 'Could not open serial port:: ' + ports[i] + "\n"
            pass
    return port_return[2]