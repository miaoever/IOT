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
		<TITLE>Noosa Shipping Monitor</TITLE>
		<meta http-equiv="refresh" content="3">
	</HEAD>
	<BODY BGCOLOR="FFFFFF">
		<a href="./">
			<img src="Noosa-1-1.jpg" alt="Noosa Warehouse Home">
		</a>
		<HR>
			<H2><a href="./shipping">Shipping Monitor</a>
				<a href="./receiving">Receiving Monitor</a>
				<a href="./robot">Robot Monitor</a></H2>
		<HR>
		<H1>Shipping Station Console</H1>
		<HR>
		<p><font size="7">{0}</font></p>
		<form action="" method="post">
			<button style="font-size:24px;height:50px;width:200px" name="done" value="shipping">Mark Done</button>
		</form>
	</BODY>
</HTML>'''
receiving_template = '''<HTML>
	<HEAD>
		<TITLE>Noosa Receiving Monitor</TITLE>
		<meta http-equiv="refresh" content="3">
	</HEAD>
	<BODY BGCOLOR="FFFFFF">
		<a href="./">
			<img src="Noosa-1-1.jpg" alt="Noosa Warehouse Home">
		</a>
		<HR>
			<H2><a href="./shipping">Shipping Monitor</a>
				<a href="./receiving">Receiving Monitor</a>
				<a href="./robot">Robot Monitor</a></H2>
		<HR>
		<H1>Receiving Station Console</H1>
		<HR>
		<p><font size="7">{0}</font></p>
		<form action="" method="post">
			<button style="font-size:24px;height:50px;width:200px" name="done" value="receiving">Mark Done</button>
		</form>
	</BODY>
</HTML>'''
maintenance_template = '''<HTML>
	<HEAD>
		<TITLE>Noosa Robot Monitor</TITLE>
	</HEAD>
	<BODY BGCOLOR="FFFFFF">
		<a href="./">
			<img src="Noosa-1-1.jpg" alt="Noosa Warehouse Home">
		</a>
		<HR>
			<H2><a href="./shipping">Shipping Monitor</a>
				<a href="./receiving">Receiving Monitor</a>
				<a href="./robot">Robot Monitor</a></H2>
		<HR>
		<H1>Robot Monitor Console</H1>
		<HR>
		<table border="1" style="width:100%">
		  <tr>
			<th>Car #</th>
			<th>In service</th> 
			<th>Reported Location</th>
			<th>Inventory</th>
			<th>Force Set</th>
		  </tr>
		  <tr>
			<td>{0}</td>
			<td>{1}</td> 
			<td>{2}</td>
			<td>{6}</td>
			<td><form action="" method="post">
				<select style="font-size:24px;height:50px;width:300px" name="car4">
					<option value=0>At receiving</option>
					<option value=1>Receiving --> Shipping</option>
					<option value=2>At shipping</option>
					<option value=3>Shipping --> Receiving</option>
				</select>
				<button style="font-size:24px;height:50px;width:200px" type="submit">Set</button>
				</form></td>
		  </tr>
		  <tr>
			<td>{3}</td>
			<td>{4}</td> 
			<td>{5}</td>
			<td>{7}</td>
			<td><form action="" method="post">
				<select style="font-size:24px;height:50px;width:300px" name="car12">
					<option value=0>At receiving</option>
					<option value=1>Receiving --> Shipping</option>
					<option value=2>At shipping</option>
					<option value=3>Shipping --> Receiving</option>
				</select>
				<button style="font-size:24px;height:50px;width:200px" type="submit">Set</button>
				</form></td>
		  </tr>
		</table>
		<form action="" method="post">
			<button style="font-size:24px;height:50px;width:400px" name="maintain" value="enter">Enter Maintenance Mode</button>
		</form>
		<form action="" method="post">
			<button style="font-size:24px;height:50px;width:400px" name="maintain" value="exit">Exit Maintenance Mode</button>
		</form>
	</BODY>
</HTML>'''

robot_template = '''<HTML>
	<HEAD>
		<TITLE>Noosa Robot Monitor</TITLE>
		<meta http-equiv="refresh" content="3">
	</HEAD>
	<BODY BGCOLOR="FFFFFF">
		<a href="./">
			<img src="Noosa-1-1.jpg" alt="Noosa Warehouse Home">
		</a>
		<HR>
			<H2><a href="./shipping">Shipping Monitor</a>
				<a href="./receiving">Receiving Monitor</a>
				<a href="./robot">Robot Monitor</a></H2>
		<HR>
		<H1>Robot Monitor Console</H1>
		<HR>
		<table border="1" style="width:100%">
		  <tr>
			<th>Car #</th>
			<th>In service</th> 
			<th>Reported Location</th>
			<th>Inventory</th>
			<th>Force Set</th>
		  </tr>
		  <tr>
			<td>{0}</td>
			<td>{1}</td> 
			<td>{2}</td>
			<td>{6}</td>
			<td>Only available under maintenance mode</td>
		  </tr>
		  <tr>
			<td>{3}</td>
			<td>{4}</td> 
			<td>{5}</td>
			<td>{7}</td>
			<td>Only available under maintenance mode</td>
		  </tr>
		</table>
		<form action="" method="post">
			<button style="font-size:24px;height:50px;width:400px" name="maintain" value="enter">Enter Maintenance Mode</button>
		</form>
		<form action="" method="post">
			<button style="font-size:24px;height:50px;width:400px" name="maintain" value="exit">Exit Maintenance Mode</button>
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
		print "serial started..."
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

			if self.path=="/robot":
				self.send_response(200)
				self.send_header('Content-type','text/html')
				self.end_headers()
				car1 = self.orderManager.cars[4]
				car2 = self.orderManager.cars[12]
				if self.orderManager.maintenance:
					self.wfile.write(maintenance_template.format(str(car1.id),car1.get_service(),
						car1.get_location(),str(car2.id),car2.get_service(),car2.get_location(),
						car1.get_inventory(),car2.get_inventory()))
				else:
					self.wfile.write(robot_template.format(str(car1.id),car1.get_service(),
						car1.get_location(),str(car2.id),car2.get_service(),car2.get_location(),
						car1.get_inventory(),car2.get_inventory()))
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
		#print(post_data)
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
		elif post_data=="maintain=enter":
			self.orderManager.enter_maintenance()
			self._set_headers()
			response = '''<html>
				<head>
				<meta http-equiv="refresh"
				content="1; url=./robot">
				</head>
				<body>
				<h1>Processing... Please wait...</h1>
				</body>
				</html>'''
			self.wfile.write(response)
		elif post_data=="maintain=exit":
			self.orderManager.exit_maintenance()
			self._set_headers()
			response = '''<html>
				<head>
				<meta http-equiv="refresh"
				content="1; url=./robot">
				</head>
				<body>
				<h1>Processing... Please wait...</h1>
				</body>
				</html>'''
			self.wfile.write(response)
		elif post_data.startswith("car4="):
			self.orderManager.force_car_location(4,int(post_data[5:]))
			self._set_headers()
			response = '''<html>
				<head>
				<meta http-equiv="refresh"
				content="1; url=./robot">
				</head>
				<body>
				<h1>Processing... Please wait...</h1>
				</body>
				</html>'''
			self.wfile.write(response)
		elif post_data.startswith("car12="):
			self.orderManager.force_car_location(12,int(post_data[6:]))
			self._set_headers()
			response = '''<html>
				<head>
				<meta http-equiv="refresh"
				content="1; url=./robot">
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