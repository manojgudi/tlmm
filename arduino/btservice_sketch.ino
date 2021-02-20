#include <SoftwareSerial.h>
SoftwareSerial EEBlue(10, 11); // RX | TX

int SWITCH_PIN = 7;
int LED_OUT = 13;
int RED_LED = 6;
int GREEN_LED = 5;
int YELLOW_LED = 4;

// Messge Codes
const char* HELLO_WORLD      = "11\n";
const String HELLO_WORLD_ACK  = "12";

const char* BUTTON_PRESS = "21\n";
const String BUTTON_PRESS_MUTE_ACK   = "22";
const String BUTTON_PRESS_UNMUTE_ACK = "23";

// received code
String receivedCode;

// Flags
boolean receivedHWAck;
boolean receivedHBAck;
boolean bootComplete;

boolean isMuted;

void setup()
{
  pinMode(SWITCH_PIN, INPUT_PULLUP);
  pinMode(LED_OUT, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(YELLOW_LED, OUTPUT);

  digitalWrite(SWITCH_PIN, 1);
  digitalWrite(LED_OUT, 0);
  digitalWrite(RED_LED, 0);
  digitalWrite(GREEN_LED, 0);
  digitalWrite(YELLOW_LED, 0);

  Serial.begin(9600);
  EEBlue.begin(9600);
  Serial.println("The bluetooth gates are open.\n Connect to HC-05 from any other bluetooth device with 1234 as pairing key!.");

  receivedHWAck = false;
  receivedHBAck = false;
  bootComplete  = false;

  receivedCode = "";

  // Assuming when the device is connected the call is muted
  isMuted = true;


}

void loop()
{
  // Check if heart world estabilished
  while (!receivedHWAck){
    EEBlue.write(HELLO_WORLD);
    // Wait for computer to respond
    delay(1000);
    receivedCode = receivedBTMessage(EEBlue);
    if (receivedCode == HELLO_WORLD_ACK){
      receivedHWAck = true;
      Serial.println("RECEIVED CODE " + receivedCode);
      Serial.println("Handshake completed.");
    }
  }

  // receivedHWAck is True here
  if (!bootComplete){
    // TODO blink RED LED light X 2
    bootComplete = true;
    Serial.println("Hardware Latched");
    blink(RED_LED, 4, 100);

  }

  int switchPinValue = digitalRead(SWITCH_PIN);
  if (switchPinValue == 0){
    Serial.println("The Switch Has Been Pressed");
    digitalWrite(SWITCH_PIN, 1);
    EEBlue.write(BUTTON_PRESS);

    // debounce
    delay(800);
    receivedCode = receivedBTMessage(EEBlue);
    if (receivedCode == BUTTON_PRESS_MUTE_ACK){

      Serial.println("Successfully muted.");
      blink(GREEN_LED, 4, 100);
      //TODO 
      // Switch LED ON
    } 
    else if (receivedCode == BUTTON_PRESS_UNMUTE_ACK){

      Serial.println("Successfully Unmuted");
      blink(YELLOW_LED, 4, 100);
    } 
    else {
      Serial.print("Failed Muting " + receivedCode); 
      blink(RED_LED, 4, 100);

    }

  }
}

/*
Blocking function call
 */
String receivedBTMessage(SoftwareSerial &bluetoothObj){
  String btMessage = "";
  if (bluetoothObj.available()){
    btMessage = bluetoothObj.readStringUntil('\n');
  }
  return btMessage;
}

void blink(int pinNumber, int times, int delayMS){

  for (int i=0; i < times; i++){
    digitalWrite(pinNumber, 1);
    delay(delayMS);
    digitalWrite(pinNumber, 0);
    delay(delayMS);

  }

}

String booleanToString(boolean variable){

  if (variable)
    return "is True";
  return "is False";

}

