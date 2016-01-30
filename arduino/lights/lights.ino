/*
lights.ino
Cabinet Lights for Arduino

Copyright (C) 2014-2016  Bob Helander

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include <DueFlashStorage.h>
DueFlashStorage dueFlashStorage;

#define RED      2 // pin for red LED
//#define GREEN    3
//#define BLUE     4
// Zone1 is pins 5,6,7
// Zone2 is pins 8,9,10
// Zone3 is pins 11,12,13

#define START_PIN RED
#define LIGHT_STATE_INDEX 12
#define COLOR_RED = 0
 
long bright[12] = { 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256};

long k, temp_value;

// Serial communication control variables
String commandString = "";        // The command being read off of the serial port
boolean commandComplete = false;  // True when the command is completely read of the serial port
long commandBufferLength = 500;   // 500 Characters should be enough

void setup () {
  bool values_set = false;
  for (int i=0; i<12; i++)  {
    if (dueFlashStorage.read(i) > 0) {
      values_set = true;
      break;
    }
  }
  
  if ( values_set == false ) {
    // Set the default values for all zones
    for (int zone=0; zone<4; zone++) {
      dueFlashStorage.write((zone*3) + 0, 255);
      dueFlashStorage.write((zone*3) + 1, 255);
      dueFlashStorage.write((zone*3) + 2, 150);
    }
    // Default to Lights off 
    dueFlashStorage.write(LIGHT_STATE_INDEX, 0);
  } 
    
  // Read if the lights were set on previously
  if (dueFlashStorage.read(LIGHT_STATE_INDEX) > 0) {
    setLightColorsFromMemory();
  } else {
    set_light_state(0);
  }
  
  // initialize serial:
  SerialUSB.begin(9600);
  // Reserve the buffer 
  commandString.reserve(commandBufferLength);
}

void setLightColorsFromMemory() {
    // Read the stored values
    for (int i=0; i<12; i++)  {
      byte value = dueFlashStorage.read(i);
      analogWrite(START_PIN + i, value);
    }
}

void serialEvent() {
  while (SerialUSB.available()) {
    // get the new byte:
    char inChar = (char)SerialUSB.read();    
    
    // if the incoming character is a newline, set a flag
    // so the main loop can do something about it:
    if (inChar == '\n') {
      commandComplete = true;
    } 
    else {
      // add it to the inputString:
      commandString += inChar;
    }
  }
}

byte hex2byte(char *a)
{
    int i;
    byte val = 0;

    for(i=0;i<2;i++)
       if(a[i] <= 57)
        val += (a[i]-48)*(1<<(4*(2-1-i)));
       else
        val += (a[i]-55)*(1<<(4*(2-1-i)));
    return val;
}

void command(String command) {
  //Serial.println(command);
  if (command == "RESET") {
    set_light_state(1);
  } else if (command == "ON") {
    set_light_state(1);
  } else if (command == "OFF") {
    set_light_state(0);
    lights_off();
  } else if (command.startsWith("COLOR ")) {
    int zone = hex2byte(&command[6]);
    int red = hex2byte(&command[8]);
    int green = hex2byte(&command[10]);
    int blue = hex2byte(&command[12]);
    
    store_color(zone, 0, red);
    store_color(zone, 1, green);
    store_color(zone, 2, blue);    
  } else if (command == "STATUS") {
    if (get_light_state() > 0) {
      SerialUSB.println("true");
    } else {
      SerialUSB.println("false");
    }
  } else if (command == "ZONE0") {
    write_color_usb(0);
  } else if (command == "ZONE1") {
    write_color_usb(1);
  } else if (command == "ZONE2") {
    write_color_usb(2);
  } else if (command == "ZONE3") {
    write_color_usb(3);
  }
}

void lights_off() {
  for (int zone=0; zone<4; zone++)  {
    set_color(zone, 0, 0, 0);
  }
}

// Set the RGB for a zone
void set_color(int zone, int red, int green, int blue) {
  int red_led = (zone * 3) + RED; 
  analogWrite(red_led, red);
  analogWrite(red_led + 1, green);  // I must have these wired incorrectly.
  analogWrite(red_led + 2, blue);   // Green should be +1 and Blue should be +2
}

byte get_color(int zone, int index) {
   return dueFlashStorage.read((zone*3)+ index);
}

void write_color_usb(int zone) {
  byte red = get_color(zone, 0);
  byte green = get_color(zone, 1);
  byte blue = get_color(zone, 2);
  SerialUSB.print(red, HEX);
  SerialUSB.print(green, HEX);
  SerialUSB.print(blue, HEX);
  SerialUSB.println("");
}
  

void store_color(int zone, int index, byte color) {
   dueFlashStorage.write((zone*3)+ index, color);
}

byte get_light_state() {
  return dueFlashStorage.read(LIGHT_STATE_INDEX);
}

void set_light_state(byte value) {
  dueFlashStorage.write(LIGHT_STATE_INDEX, value);
}

void exec_instruction() {
  if (get_light_state()  > 0) {
    for (int i=0; i<4; i++)  {
      byte red = get_color(i, 0);
      byte green = get_color(i, 1);
      byte blue = get_color(i, 2);
      set_color(i, red, green, blue);
    }
  }
}

void loop() {
  if (SerialUSB.available()) serialEvent();
  
  if (commandComplete) {
    command(commandString);
    // clear the string:
    commandString = "";
    commandComplete = false;
  }
    
  exec_instruction();
}