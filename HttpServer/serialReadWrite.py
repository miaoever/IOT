###################################################################################################################
# File: serialwriter.py
# Course: 17640
# Project: IoT Order Fulfillment Center
# Copyright: Copyright (c) 2018 Carnegie Mellon University (ajl)
# Versions:
#	1.0 April 2018 - Initial write (ajl).
#
# Description: This class serves as an example for how to write an application that can write serial data to
# an external device. The intent is for this to illustrate how to write data to an Arduino software serial
# port. This example could be used as a basis for writing an application to send command to fulfillment
# center robots.
#
# Parameters: Port or device file
#
# Internal Methods:
#  None
#
# External Dependencies:
#   - python 2.7
#	- time
#	- serial ## pyserial-3.2.1 library
###################################################################################################################

import sys
import time
import serial 
import thread

class SerialReadWrite(object):


	def __init__(self, port, orderManager):
		self.ser = serial.Serial(
			port=port,
			baudrate=9600,
			parity=serial.PARITY_NONE,
			stopbits=serial.STOPBITS_ONE,
			bytesize=serial.EIGHTBITS
		)
		self.orderManager = orderManager
		time.sleep(1)

	def carMove(self, carNo):
		num = "04" if carNo==4 else "12"
		message = num + "m"
		b = str.encode(message)						# Puts the message into bytes
		self.ser.write(b)								# Writes the bytes to the specified port 
		self.ser.flush()

	def listen(self):
		while True:
			if self.ser.inWaiting() > 0:				# Check to see if anything is in the buffer					
				line = self.ser.readline()			# Read the buffer
				if line=="12s\n":
					print "Car 12 arrives at shipping"
					self.orderManager.cars[12].set_location(2)
				elif line=="12r\n":
					print "Car 12 arrives at receiving"
					self.orderManager.cars[12].set_location(0)
				elif line=="04s\n":
					print "Car 4 arrives at shipping"
					self.orderManager.cars[4].set_location(2)
				elif line=="04r\n":
					print "Car 4 arrives at receiving"
					self.orderManager.cars[4].set_location(0)
				#print('read::' + line)
			time.sleep(1)
			#

	def run(self):
		thread.start_new_thread(self.listen,())
								

