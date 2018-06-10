"""
Very simple HTTP server in python.
Usage::
	./dummy-web-server.py [<port>]
Send a GET request::
	curl http://localhost
Send a HEAD request::
	curl -I http://localhost
Send a POST request::
	curl -d "foo=bar&bin=baz" http://localhost
"""
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from serialReadWrite import SerialReadWrite
from os import curdir, sep
import SocketServer
from OrderManager import *
import sys
import time
import serial
import thread

shipping_template = '''<HTML>
	<HEAD>
		<TITLE>Noosa Receiving Monitor</TITLE>
		<meta http-equiv="refresh" content="5">
	</HEAD>
	<BODY BGCOLOR="FFFFFF">
		<a href="./">
  			<img src="Noosa-1-1.jpg" alt="Noosa Warehouse Home">
		</a>
		<HR>
			<H1><a href="./shipping">Shipping Monitor</a></H1>
			<H1><a href="./receiving">Receiving Monitor</a></H1>
		<HR>
		<p><big>{0}</big></p>
		<form action="" method="post">
    		<button name="done" value="shipping">Mark Done</button>
		</form>
	</BODY>
</HTML>'''
receiving_template = '''<HTML>
	<HEAD>
		<TITLE>Noosa Receiving Monitor</TITLE>
		<meta http-equiv="refresh" content="5">
	</HEAD>
	<BODY BGCOLOR="FFFFFF">
		<a href="./">
  			<img src="Noosa-1-1.jpg" alt="Noosa Warehouse Home">
		</a>
		<HR>
			<H1><a href="./shipping">Shipping Monitor</a></H1>
			<H1><a href="./receiving">Receiving Monitor</a></H1>
		<HR>
		<p><big>{0}</big></p>
		<form action="" method="post">
    		<button name="done" value="receiving">Mark Done</button>
		</form>
	</BODY>
</HTML>'''

class NoosaServer:
	def __init__(self, server_address, serialport):
		self.orderManager = OrderManager()
		NoosaHandler.orderManager = self.orderManager
		self.serial = SerialReadWrite(serialport,self.orderManager)
		self.orderManager.setSerial(self.serial)
		self.server = HTTPServer(server_address, NoosaHandler)
	def serve_forever(self):
		self.serial.run()
		print "serial run"
		self.server.serve_forever()

class NoosaHandler(BaseHTTPRequestHandler):
	orderManager = None

	def _set_headers(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

	def do_GET(self):
		if self.path=="/":
			self.path="/homepage.html"

		try:
			#Check the file extension required and
			#set the right mime type

			#self.orderManager.simulate()

			sendReply = False
			if self.path=="/shipping":
				self.send_response(200)
				self.send_header('Content-type','text/html')
				self.end_headers()
				self.wfile.write(shipping_template.format(self.orderManager.get_unload_instruction()))
				return

			if self.path=="/receiving":
				self.send_response(200)
				self.send_header('Content-type','text/html')
				self.end_headers()
				self.wfile.write(receiving_template.format(self.orderManager.get_loading_instruction()))
				return

			if self.path.endswith(".html"):
				mimetype='text/html'
				sendReply = True
			if self.path.endswith(".jpg"):
				mimetype='image/jpg'
				sendReply = True
			if self.path.endswith(".gif"):
				mimetype='image/gif'
				sendReply = True
			if self.path.endswith(".js"):
				mimetype='application/javascript'
				sendReply = True
			if self.path.endswith(".css"):
				mimetype='text/css'
				sendReply = True

			if sendReply == True:
				#Open the static file requested and send it
				f = open(curdir + sep + self.path) 
				self.send_response(200)
				self.send_header('Content-type',mimetype)
				self.end_headers()
				self.wfile.write(f.read())
				f.close()
			return


		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)

	def do_HEAD(self):
		self._set_headers()
		
	def do_POST(self):
		content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
		post_data = self.rfile.read(content_length) # <--- Gets the data itself
		if post_data=="done=receiving":
			self.orderManager.finish_loading_instruction()
			self._set_headers()
			response = '''<html>
				<head>
				<meta http-equiv="refresh"
				content="1; url=./receiving">
				</head>
				<body>
				<h1>Processing... Please wait...</h1>
				</body>
				</html>'''
			self.wfile.write(response)			
		elif post_data=="done=shipping":
			self.orderManager.finish_unload_instruction()
			self._set_headers()
			response = '''<html>
				<head>
				<meta http-equiv="refresh"
				content="1; url=./shipping">
				</head>
				<body>
				<h1>Processing... Please wait...</h1>
				</body>
				</html>'''
			self.wfile.write(response)			
		else:
			self._set_headers()
			self.wfile.write("<html><body><h1>Unexpected post. Please go back.</h1></body></html>")
		
def run(serialport):
	server_address = ('', 80)
	httpd = NoosaServer(server_address, serialport)
	print 'Starting httpd...'
	httpd.serve_forever()

if __name__ == "__main__":
	from sys import argv

	if len(argv) == 2:
		run(serialport=int(argv[1]))
	else:
		run("/dev/tty.usbserial")
