#include <SPI.h>
#include <Ethernet.h>

// network configuration.  gateway and subnet are optional.

 // the media access control (ethernet hardware) address for the shield:
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };  
//the IP address for the shield:
byte ip[] = { 10, 29, 37, 95 };    
// the router's gateway address:
byte gateway[] = { 10, 29, 37, 1 };
// the subnet:
byte subnet[] = { 255, 255, 255, 0 };

EthernetServer server = EthernetServer(8888);

void setup()
{
  pinMode(13, OUTPUT);
  
  pinMode(2, INPUT);   // Zone: 1
  pinMode(3, INPUT);   // Zone: 2
  pinMode(4, INPUT);   // Zone: 3
  pinMode(5, INPUT);   // Zone: 4
  pinMode(6, INPUT);   // Zone: 5
  pinMode(7, INPUT);   // Zone: 6
  pinMode(8, INPUT);   // Zone: 7
  pinMode(9, INPUT);   // Zone: 8
  pinMode(10, INPUT);  // Zone: 9
  
  // initialize the ethernet device
  Ethernet.begin(mac, ip, gateway, subnet);

  // start listening for clients
  server.begin();
} 

String read_zone_status() {
  char zone_array[] = {LOW,LOW,LOW,LOW,LOW,LOW,LOW,LOW,LOW};
  
  int array_index = 0;
  int pin_index = 2;  // Start at pin 2 and read to 8
  for (; pin_index < 11; ++pin_index, ++array_index) {
    zone_array[array_index] = digitalRead(pin_index);
  }
  
  String status_message = "0:0:0:0:0:0:0:0:0";

  for (array_index=0; array_index < 9; ++array_index) {
    if (zone_array[array_index] == HIGH) {
      status_message[array_index*2] = '1';
    }
  }  
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

void loop()
{
  // if an incoming client connects, there will be bytes available to read:
  EthernetClient client = server.available();
  if (client == true) {
    // Turn on on-board LED
    digitalWrite(13, HIGH);

    String message = read_message(client);

    if (message == "status") {
      client.println(read_zone_status());
    }
    else if (message == "message2") {
      client.println("success:2");
    }
    else if (message == "message3") {
      client.println("success:3");
    }
    
    client.stop();
    // Turn off on-board LED
    digitalWrite(13, LOW);
  }
}

