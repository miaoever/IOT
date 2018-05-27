import sys
import time
import serial 
from pynput.keyboard import Key, Listener
from serialports import get_port
# Here we define the serial port. This reflects the settings for the software serial port on the arduino.
# Please refer to the companion arduino code: SoftSerialRead.ino. Note that no errors are trapped here in the 
# name of brevity. If the comm port/device doesn't exist, it will crash here. For your production code you should
# probably add error handling here (try-catches).

ser = serial.Serial(
    port=get_port(),
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)

# Wait a couple of seconds for things to settle (typical in the embedded world ;-)

time.sleep(1)
print 'Enter listener'


def is_key(key):
    if not (key=='a' or key=='w' or key=='s' or key=='d'):
        return False
    return True

def on_press(key):
    if is_key(key.char):
        print('{0} pressed'.format(key))
        b = str.encode((key.char+"").encode('utf-8'))					# Puts the message into bytes
        ser.write(b)								# Writes the bytes to the specified port 
        ser.flush()									# We clear the port
    
def on_release(key):
    if key == Key.esc:
        # Stop listener
        return False
with Listener(
	on_press = on_press,
    on_release = on_release) as listener: 
    try:
        listener.join()
    except Exception as e:
        print('{0} was pressed'.format(e.args[0]))
