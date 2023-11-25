#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <SPI.h>
#include <MFRC522.h>
#define SS_PIN D8
#define RST_PIN D0

//MFRC522 lines for the RFID
MFRC522 rfid(SS_PIN, RST_PIN); // Instance of the class
MFRC522::MIFARE_Key key;

// Init array that will store new NUID
byte nuidPICC[4];

// String for the hex value of rfid card
String hexRfid;

//credentials for the mqtt server
const char* ssid = "iPhone (44)";
const char* password = "sukablyat";
const char* mqtt_server = "172.20.10.2";


//Vanier wifi
WiFiClient vanieriot;
PubSubClient client(vanieriot);

//photoresistor pin
const int pResistor = A0;

//light variables
String lightInt_str;
char lightInt[50];

//Setup the wifi connection for vanier
void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("WiFi connected - ESP-8266 IP address: ");
  Serial.println(WiFi.localIP());
  
}

//Print topic messages 
void callback(String topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String messagein;
  
  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
    messagein += (char)message[i];
  }

}

//Connecting to mqtt server
void reconnect() {
  while (!client.connected()) {
    Serial.print("\nAttempting MQTT connection...");
    if (client.connect("vanieriot")) {
      Serial.println("connected");
    
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 3 seconds");
      // Wait 5 seconds before retrying
      delay(3000);
    }
  }
}


//initiate all the connections(mqtt server, wifi, board inputs)
void setup() {

  Serial.begin(115200);
  pinMode(pResistor, INPUT);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  //rfid code
  SPI.begin(); // Init SPI bus
  rfid.PCD_Init(); // Init MFRC522
  Serial.println();
  Serial.print(F("Reader :"));
  rfid.PCD_DumpVersionToSerial();
  
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }

  Serial.println();
  Serial.println(F("This code scan the MIFARE Classic NUID."));
  Serial.print(F("Using the following key:"));
  getHex(key.keyByte, MFRC522::MF_KEY_SIZE);
}

//loop this code
void loop() {

  //read variables of the light
  int lightIntVal = analogRead(pResistor);
  lightInt_str = String(lightIntVal);
  lightInt_str.toCharArray(lightInt, lightInt_str.length() + 1);

  // Reset the loop if no new card present on the sensor/reader. This saves the entire process when idle.
if ( ! rfid.PICC_IsNewCardPresent())
 return;
// Verify if the NUID has been readed
if ( ! rfid.PICC_ReadCardSerial())
 return;
Serial.print(F("PICC type: "));
MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);
Serial.println(rfid.PICC_GetTypeName(piccType));
// Check is the PICC of Classic MIFARE type
if (piccType != MFRC522::PICC_TYPE_MIFARE_MINI &&
 piccType != MFRC522::PICC_TYPE_MIFARE_1K &&
 piccType != MFRC522::PICC_TYPE_MIFARE_4K) {
 Serial.println(F("Your tag is not of type MIFARE Classic."));
 return;
}
if (rfid.uid.uidByte[0] != nuidPICC[0] ||
 rfid.uid.uidByte[1] != nuidPICC[1] ||
 rfid.uid.uidByte[2] != nuidPICC[2] ||
 rfid.uid.uidByte[3] != nuidPICC[3] ) {
 Serial.println(F("A new card has been detected."));
 // Store NUID into nuidPICC array

 for (byte i = 0; i < 4; i++) {
  nuidPICC[i] = rfid.uid.uidByte[i];
 }
 Serial.println(F("The NUID tag is:"));
 Serial.print(F("In hex: "));
 getHex(rfid.uid.uidByte, rfid.uid.size);
 Serial.println();
 Serial.print(F("In dec: "));
 printDec(rfid.uid.uidByte, rfid.uid.size);
 Serial.println();
}
else Serial.println(F("Card read previously."));
// Halt PICC
rfid.PICC_HaltA();
// Stop encryption on PCD
rfid.PCD_StopCrypto1();

  
  //reconnect the client if not connected
  if (!client.connected()) {
    reconnect();
  }
  
  if(client.loop()){

    //publish the client topic for photoresistor variables and light variables
    client.connect("vanieriot");
    client.publish("ESP/pResistor", lightInt);
    client.publish("rfid_reader", getHex(rfid.uid.uidByte, rfid.uid.size).c_str());
  
  delay(1000);
  }

//reconnect the client if not connected
  if (!client.connected()) {
    reconnect();
  }
}

/**
 Helper routine to dump a byte array as hex values to Serial.
*/
String getHex(byte *buffer, byte bufferSize) {
 String id = "";
for (byte i = 0; i < bufferSize; i++) {
 id += buffer[i] < 0x10 ? " 0" : " ";
 id += String(buffer[i], HEX);
 
// Serial.print(buffer[i] < 0x10 ? " 0" : " ");
// Serial.print(buffer[i], HEX);
 }
 return id;
 //publish the hex to the mqtt server
}
/**
 Helper routine to dump a byte array as dec values to Serial.
*/
void printDec(byte *buffer, byte bufferSize) {
  String id = "";
for (byte i = 0; i < bufferSize; i++) {
 
 id += buffer[i] < 0x10 ? " 0" : " ";
 id += String(buffer[i], DEC);
 
// Serial.print(buffer[i] < 0x10 ? " 0" : " ");
// Serial.print(buffer[i], DEC);
 }
 Serial.print(id);
}
