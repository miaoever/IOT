/* File: RadioXmit
** Course: 17640
** Project: IoT Order Fulfillment Center
** Copyright: Copyright (c) 2018 Carnegie Mellon University (ajl)
** Versions:
** 1.0 April 2018 - Initial write (ajl).
**
** Description: This class serves as an example for how to write an 
** application for the robot to use the radio to send data to a PC/Mac
** via the radio base station.
** This example could be used as a basis for writing an application to 
** control and get status to-from Arduinos on the order fulfillment robots.
**
** Parameters: None
**
** Internal Methods:
**  None
**
** External Dependencies: 
**
**  SPI.h - Serial Peripherial Interface (SPI) protocol.
**  nRF24L01.h - Radio library
**  RF24.h - Radio library
**  
** See radio documentation at: https://maniacbug.github.io/RF24/classRF24.html 
*/

#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <SoftwareSerial.h>
#define RX 9                            // Pin used for the receive port on the Arduino
#define TX 10                           // Pin used for the transmit port on the Arduino

RF24 radio(7, 8);                 // Chip enable (7), Chip Select (8)
const byte address[6] = "00004";  // Radio address - use only the channels that match the
                                  // numbers on your robots.
SoftwareSerial mySerial(RX, TX, true);  // Here we define the serial port object
char character;                         // Character read from the serial port

void setup() 
{
  Serial.begin(9600);
  radio.begin();                  // Instantiate the radio object
  mySerial.begin(9600); // Open the software serial port. Once we open the port we
                      // print a message and wait a second for things to settle
                      // down.
                          
  if (!radio.isChipConnected())
  {
      while(!radio.isChipConnected());
  }
  
  
//  radio.openReadingPipe(0, address);  // Open the radio pipe using your address (read about pipes and channels)
//  radio.setPALevel(RF24_PA_MIN);      // Set the power level. Since the bots and the radio base station are close I use min power
//  radio.startListening();             // Go into receive mode.
//  Serial.println("Radio Read Ready...");
}

void loop()                        // We just send hello world broadcasts every second
{
  while(mySerial.available())
  {
    //open write
    radio.openWritingPipe(address);  // Open the radio pipe using your address (read about pipes and channels)
    radio.setPALevel(RF24_PA_MIN);   // Set the power level. Since the bots and the radio base station are close I use min power
    radio.stopListening();           // Now we listen for messages...
  
    char content[16] = {};
    mySerial.readBytes(content, 16);   // Here is where we read the data
    Serial.println(content);
    radio.write(&content, sizeof(content));

     //open read
    radio.openReadingPipe(0, address);  // Open the radio pipe using your address (read about pipes and channels)
    radio.setPALevel(RF24_PA_MIN);      // Set the power level. Since the bots and the radio base station are close I use min power
    radio.startListening();             // Go into receive mode.
    Serial.println("Radio Read Ready...");

  }

  

  while (radio.available())
  {
    char cmd[10] = "";
    radio.read(&cmd, 3);
    Serial.print("Receive command: ");
    Serial.println(cmd);
    mySerial.write(cmd);
    //delay(1000);
  }
}
