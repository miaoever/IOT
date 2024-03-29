
/****************************************************************
  File: LineFollowDemo
  Project: IoT Course
  Copyright: Copyright (c) 2018 Anthony J. Lattanze
  1.0 April 2018 - Initial version

  Description:

  This program runs on the IoT bots with two continous servos, a
  Ping))) sonar, and 3 QTI Ir sensors.

  Compilation and Execution Instructions: Compile using
  Arduino IDE.

  Parameters: None

  Internal Methods:
  long ReadQTI(int pin) - Reads the IR sensor, returns a value
                         between 0 that indicated the lightness or
                         darkness under the IR sensor (0=white)
  long ReadSonarInches (int pin) - Reads the sonar and returns
                                   a value indicating the distanc
                                   of an object infront of the
                                   robot.
  boolean Obstacle(int pin) - Returns true if there is an obstacle
                              2" or less in front of the robot.
                              Otherwise, it returns false.
*****************************************************************/

#include <Servo.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <stdlib.h>

#define SonarPin 2        // Sonar pin
#define OnBoardLED 13     // On board LED for signalling and debugging
#define RightServo 5      // Right servo pin
#define LeftServo 6       // left servo pin
#define LeftQTIPin A0     // Left IR sensor pin
#define CenterQTIPin A1   // Center IR sensor pin
#define RightQTIPin A2    // Right IR sensor pin
#define ServoStop 90      // PWM value to stop the servos
//----------------- Parallax Servos---------------------------------------
#define CWSFull 70         // PWM value for clockwise servo motion - High Speed 
#define CCWSFull 110      // PWM value for counter clockwise servo motion - High Speed 
#define CWSMid 80         // PWM value for clockwise servo motion - Mid Speed
#define CCWSMid 100       // PWM value for counter clockwise servo motion - Mid Speed
#define CWSSlow 85        // PWM value for clockwise servo motion - Slow Speed
#define CCWSSlow 95       // PWM value for counter clockwise servo motion - Slow Speed

#define RWOffSet  0       // Right and left servo velocity offsets. Compensates for 
#define LWOffSet  0       // differences in servos velocities that can't be fixed in calibration.
// Helps bots maintain straight line of travel.

#define Threshold 100     // This is the threshold from white to black. You will have to adjust this 
// for each bot based on tests performed with the QTI tests. Any values less
// than Threshold will be considered white. Above Threshold, black.

#define CommandDuration 100   // The duration time for executing a command.

// Parameters

int leftQti;              // Left IR sensor value
int centerQti;            // Center IR sensor value
int rightQti;             // Right IR sensor value

Servo leftservo;          // Left servo object
Servo rightservo;         // Right servo object

RF24 radio(7, 8);                     // Chip enable (7), Chip Select (8)
const byte address[6] = "00004";      // Radio address - use only the channels that match the
// numbers on your robots.

// Set up

void setup()
{
  // Initialize the Serial port:
  Serial.begin(9600);
  leftservo.attach(LeftServo);
  rightservo.attach(RightServo);
  leftservo.write(ServoStop);
  rightservo.write(ServoStop);

  pinMode(OnBoardLED, OUTPUT);
  delay(1000);

  // Initialize the Radio
  radio.begin();                      // Instantiate the radio object

  if (!radio.isChipConnected())       // See if the radio is connect. Loop while its not connected
  {
    Serial.print("RADIO NOT CONNECTED!");
    while (!radio.isChipConnected());
  }

  startRadioRead();
}

void loop()
{
  if (radio.available()) {

    char text[32] = "";
    radio.read(&text, sizeof(text));
    int len = strlen(text);
    switch (text[len - 1]) {
      case 'w': forward(); delay(CommandDuration); break;
      case 'a': turnLeft(); delay(CommandDuration); break;
      case 's': backward(); delay(CommandDuration); break;
      case 'd': turnRight(); delay(CommandDuration); break;
      default:
        Serial.print(text[len - 1]);
        Serial.println(" Unknown command!");
    }

  } else {
    servoStop();
  }

} // loop

void forward()
{
  // centered on the line
  leftservo.write(CCWSFull + LWOffSet);
  rightservo.write(CWSFull + RWOffSet);
  Serial.println( "forward" );

  radioSend("Move Forward");
}

void turnLeft()
{
  // Drifted right
  leftservo.write(91);    // #TODO, magic number
  rightservo.write(83);   // #TODO, magic number
  Serial.println( "jog right" );

  radioSend("Turn Left");
}

void turnRight()
{
  // Drifted left
  leftservo.write(97);    // #TODO, magic number
  rightservo.write(89);   // #TODO, magic number
  Serial.println( "jog left" ); 

  radioSend("Turn Right");
}

void backward()
{
  // centered on the line
  leftservo.write(CWSFull + RWOffSet);
  rightservo.write(CCWSFull + LWOffSet);
  Serial.println( "backward" );

  radioSend("Move Backward");
}

void servoStop()
{
  leftservo.write(ServoStop); 
  rightservo.write(ServoStop);
}

void atShipping()
{
  radioSend("At Shipping!");

  // At shipping
  Serial.println( "shipping" );
  leftservo.write(ServoStop);
  rightservo.write(ServoStop);
  delay(3000);
  leftservo.write(CCWSMid + LWOffSet);
  rightservo.write(CWSMid + RWOffSet);
  delay(500);
}

void atReceiving()
{
  radioSend("At Receiving");

  // At receiving
  Serial.println( "receiving" );
  leftservo.write(ServoStop);
  rightservo.write(ServoStop);
  delay(3000);
  leftservo.write(CCWSMid + LWOffSet);
  rightservo.write(CWSMid + LWOffSet);
  delay(500);
}

void startRadioRead()
{
  radio.openReadingPipe(0, address);  // Open the radio pipe using your address (read about pipes and channels)
  radio.setPALevel(RF24_PA_MIN);      // Set the power level. Since the bots and the radio base station are close I use min power
  radio.startListening();             // Go into receive mode.
  Serial.println("Radio Read Ready...");
  // delay(1000);
}

void startRadioWrite()
{
  radio.stopListening();           // Now we listen for messages...
  radio.openWritingPipe(address);  // Open the radio pipe using your address (read about pipes and channels)
  radio.setPALevel(RF24_PA_MIN);   // Set the power level. Since the bots and the radio base station are close I use min power
  Serial.println("Radio Write Ready...");
  // delay(1000);
}

void radioSend(const char * text)
{
  // startRadioWrite();
  // radio.startWrite(text, strlen(text), false);
}

/****************************************************************
  ReadQTI (int pin)

  Parameters:
               int pin - the pin on the Arduino where the QTI
                         sensor is connected.
  Description:
   - Reads the shade of the area under the QTI
  sensor by determines how long it takes an on-board capactior
  to charge/discharge. This method initalizes the sensor pin as
  output and charges the capacitor on the QTI. The QTI emits IR
  light which is reflected off of any surface in front of the
  sensor. The amount of IR light reflected back is detected by
  the IR resistor on the QTI. This is the resistor that the
  capacitor discharges through. The amount of time it takes to
  discharge determines how much light, and therefore the
  lightness or darkness of the material in front of the QTI
  sensor.

  Zero or lower single digit values indicate white
  Higher values indicate dark
****************************************************************/

long ReadQTI(int sensorIn)
{
  long duration = 0;
  pinMode(sensorIn, OUTPUT);          // Sets pin as OUTPUT
  digitalWrite(sensorIn, HIGH);       // Pin HIGH
  delay(1);                           // Allow capacitor to fully discharge
  pinMode(sensorIn, INPUT);           // Sets pin as INPUT
  digitalWrite(sensorIn, LOW);        // Pin LOW
  while (digitalRead(sensorIn))
    duration++;                       // LOW (cap discharges)

  return duration;                    // Returns the duration of the pulse
}

/****************************************************************
  boolean Obstacle (int pin)

  Parameters: None
               int pin - the pin on the Arduino where the sonar
                         is connected.
  Description:
  Issues a command to the sonar checks for objects in front of the
  robot. If there is an obstacal within 2 inches this method will
  return true, otherwise it will return false.
****************************************************************/
boolean Obstacle( int pin )
{
  if (ReadSonarInches(SonarPin) <= 3 )
  {
    return ( true );

  } else {
    return ( false );
  }

}

/****************************************************************
  ReadSonarInches (int pin)

  Parameters:
               int pin - the pin on the Arduino where the sonar
                         is connected.
  Description:
  Issues a command for the sonar to perform a ping-echo to
  determine the distance of any objects in front of the sonar. A
  pulse triggers the ping, then we count how long it takes to
  receive the return echo. The ping))) sonar will measure between
  1 inch and 144 inches. This routine returns distance in inches.

****************************************************************/

long ReadSonarInches( int pin )
{

  long duration;  // Duration of the ping/echo
  long inches;    // Distance in inches


  // The sonar is triggered by a HIGH pulse of 2 or more microseconds.
  // Give a short LOW pulse beforehand to ensure a clean HIGH pulse:

  pinMode(pin, OUTPUT);
  digitalWrite(pin, LOW);
  delayMicroseconds(2);
  digitalWrite(pin, HIGH);
  delayMicroseconds(5);
  digitalWrite(pin, LOW);

  // The same pin is used to read the signal from the sonar. A HIGH
  // pulse whose duration is the time (in microseconds) from the sending
  // of the ping to the reception of its echo off of an object.

  pinMode(pin, INPUT);
  duration = pulseIn(pin, HIGH);

  // Sound travels at 1130 feet per second, so there are 73.746 microseconds per inch.
  // This gives the distance travelled by the ping, outbound and return, so we divide
  // by 2 to get the distance to the obstacle.

  if (duration / 74 / 2 == 0 )
  {
    digitalWrite(OnBoardLED, HIGH);
    delay(500);
    digitalWrite(OnBoardLED, LOW);
  }
  return duration / 74 / 2;
}

