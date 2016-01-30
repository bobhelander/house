/*
sprinklersystem.ino
Irrigation system control methods

Copyright (C) 2013-2016  Bob Helander

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

#include <SPI.h>
#include <Ethernet.h>

// network configuration.  gateway and subnet are optional.

 // the media access control (ethernet hardware) address for the shield:
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xEF };  
//the IP address for the shield:
byte ip[] = { 10, 29, 37, 96 };    
// the router's gateway address:
byte gateway[] = { 10, 29, 37, 1 };
// the subnet:
byte subnet[] = { 255, 255, 255, 0 };

EthernetServer server = EthernetServer(8888);

int relay01 = 7;
int relay02 = 6;
int relay03 = 5;
int relay04 = 4;

int relay_array[] = {relay01, relay02, relay03, relay04};

unsigned long cycle_end = 0;
boolean running_cycle = false;

int server_reset_timeout = 50000
int reset_timeout = server_reset_timeout;

void setup()
{
  pinMode(13, OUTPUT);
  
  pinMode(relay01, OUTPUT);  // Zone: 1
  pinMode(relay02, OUTPUT);  // Zone: 2
  pinMode(relay03, OUTPUT);  // Zone: 3
  pinMode(relay04, OUTPUT);  // Zone: 4

  // initialize the ethernet device
  Ethernet.begin(mac, ip, gateway, subnet);

  // start listening for clients
  server.begin();
} 

void all_off() {
  digitalWrite(relay01, 0); 
  digitalWrite(relay02, 0); 
  digitalWrite(relay03, 0); 
  digitalWrite(relay04, 0); 
}

void monitor_running_cycle() {
  if ( running_cycle == true && millis() > cycle_end ) {
    end_cycle();
  }
}

void end_cycle() {
    all_off();
    running_cycle = false;
    cycle_end = 0;
}

void start_cycle(unsigned long milliseconds) {
  running_cycle = true;
  cycle_end = millis() + milliseconds;
  if ((cycle_end + 60000) < millis()) { 
    // will overflow while cycle is running
    // do not start cycle
    end_cycle();
  }
}

String read_zone_status() {
  char zone_array[] = {LOW,LOW,LOW,LOW};
  for (int array_index = 0; array_index < 4; ++array_index) {
    zone_array[array_index] = digitalRead(relay_array[array_index]);
  }
  
  String status_message = "0:0:0:0:";

  for (int array_index=0; array_index < 4; ++array_index) {
    if (zone_array[array_index] == HIGH) {
      status_message[array_index*2] = '1';
    }
  }
  
  String milliseconds_left = "0";
  
  if (running_cycle == true) {
    milliseconds_left = String(cycle_end - millis(), DEC);
  }
  
  status_message += milliseconds_left;
  
  return status_message;
}

String read_message(EthernetClient& client) {
  String incoming_message = "";

  char nextChar = client.read();
  while (nextChar != -1) {
    incoming_message += nextChar;
    nextChar = client.read();
  }
  return incoming_message;
} 

String set_relay(int relay_number, int state) {
  digitalWrite(relay_number, state); 
  return "Done";
}

void reset_server() {
  server = EthernetServer(8888);
  setup();
}

void loop()
{
  // if an incoming client connects, there will be bytes available to read:
  EthernetClient client = server.available();
  if (client == true) {
    // Turn on on-board LED
    digitalWrite(13, HIGH);
    
    // Received message, restart counter
    reset_timeout = server_reset_timeout;

    String message = read_message(client);

    if (message == "zone01-on") {
      client.println(set_relay(relay01, HIGH));
    }
    else if (message == "zone01-off") {
      client.println(set_relay(relay01, LOW));
    }
    else if (message == "zone02-on") {
      client.println(set_relay(relay02, HIGH));
    }
    else if (message == "zone02-off") {
      client.println(set_relay(relay02, LOW));
    }
    else if (message == "zone03-on") {
      client.println(set_relay(relay03, HIGH));
    }
    else if (message == "zone03-off") {
      client.println(set_relay(relay03, LOW));
    }
    else if (message == "zone04-on") {
      client.println(set_relay(relay04, HIGH));
    }
    else if (message == "zone04-off") {
      client.println(set_relay(relay04, LOW));
    }
    else if (message == "endcycle") {
      end_cycle();
      client.println(read_zone_status());
    }
    else if (message.startsWith("startcycle-")) {
      unsigned long milliseconds = long(message.substring(11).toInt());
      start_cycle(milliseconds);
      client.println(read_zone_status());
    }

    else if (message == "status") {
      client.println(read_zone_status());
    }
    
    client.stop();
    // Turn off on-board LED
    digitalWrite(13, LOW);
  }
  
  monitor_running_cycle();
  
  reset_timeout--;
  if (reset_timeout < 0) {
    reset_server();
    reset_timeout = server_reset_timeout;
  }  
}

