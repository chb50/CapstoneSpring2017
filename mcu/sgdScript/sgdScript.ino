// NTAG2x3 cards have 39*4 bytes of user pages (156 user bytes),
// starting at page 4 ... larger cards just add pages to the end of
// this range:

// See: http://www.nxp.com/documents/short_data_sheet/NTAG203_SDS.pdf

// TAG Type       PAGES   USER START    USER STOP
// --------       -----   ----------    ---------
// NTAG 203       42      4             39
// NTAG 213       45      4             39
// NTAG 215       135     4             129
// NTAG 216       231     4             225 


#include "Arduino.h"
#include <smartgun.h>
#include <EEPROM.h>
#include <assert.h>
#include <Wire.h>
#include <SPI.h>
#include <WiFi101.h>
#include <Adafruit_PN532.h>

#define TABLE_SIZE 1024
#define ENTRY_COUNT 10
#define DB_START 0 //the adress in which the database starts

#define FIRE_BUTTON 25
#define MODE 23

//for wifi
#define MEGA_CS 44
#define MEGA_IRQ 21
#define MEGA_RST 46
#define PORT 9999

struct entry {
  //800 bytes for 10 entries
  uint8_t id; //the index of the row entry in the database
  char* userName; //nickname for the user of this nfc tag
  uint8_t* nfcTag; //7 numbers for nfc tag
}
entry;

// The read and write handlers for using the EEPROM Library
void writer(unsigned long address, byte data)
{
  EEPROM.write(address, data);
}

byte reader(unsigned long address)
{
  return EEPROM.read(address);
}

// Create an SGD object with the appropriate write and read handlers for E(smartGun.db) object
SGD smartGun(&writer, &reader);

/***NFC STUFF ***/
/* this is coded using I2C communication,
 *  if needed, can also us SPI comm
 */

// If using the breakout or shield with I2C, define just the pins connected
// to the IRQ and reset lines.  Use the values below (2, 3) for the shield!
#define PN532_IRQ   (2)
#define PN532_RESET (3)  // Not connected by default on the NFC Shield

// Or use this line for a breakout or shield with an I2C connection:
Adafruit_PN532 nfc(PN532_IRQ, PN532_RESET);

#if defined(ARDUINO_ARCH_SAMD)
// for Zero, output on USB Serial console, remove line below if using programming port to program the Zero!
// also change #define in Adafruit_PN532.cpp library file
   #define Serial SerialUSB
#endif

uint8_t recordId = 1;

/*Wifi Stuff*/
char ssid[] = "HTC One_M8_BC20"; //  your network SSID (name)
char pass[] = "ClapOn88";

int keyIndex = 0;            // your network key Index number (needed only for WEP)
int z = 0;

int status = WL_IDLE_STATUS;
// if you don't want to use DNS (and reduce your sketch size)
// use the numeric IP instead of the name for the server:
IPAddress server(192,168,1,31);  // numeric IP for Google (no DNS)
//char server[] = "www.google.com";    // name address for Google (using DNS)

// Initialize the Ethernet client library
// with the IP address and port of the server
// that you want to connect to (port 80 is default for HTTP):
WiFiClient client;

void setup(void) {
  Serial.begin(9600);
  while (!Serial);
  Serial.println("Hello!");

  Serial.println("Extended Database Library + Arduino Internal EEPROM Demo");
  Serial.println();

  Serial.print("Smart gun ID: ");
  Serial.println(smartGun.getSgdId());

  randomSeed(analogRead(0));
  
  // create table at with starting address 0
  if((smartGun.db)->open(DB_START) != EDB_OK) { 
    Serial.println("Database does not exist on this device");
    Serial.println("Creating database");
    (smartGun.db)->create(DB_START, TABLE_SIZE, sizeof(entry));
  } else {
    deleteAll();
    Serial.println("Database reset");
  }
  Serial.println("DONE");
  
  nfc.begin();

  uint32_t versiondata = nfc.getFirmwareVersion();
  
  if (! versiondata) {
    Serial.print("Didn't find PN53x board");
    while (1); // halt
  }

  /*WIFI SETUP*/
  WiFi.setPins(MEGA_CS,MEGA_IRQ,MEGA_RST);
  
  // Got ok data, print it out!
  Serial.print("Found chip PN5"); Serial.println((versiondata>>24) & 0xFF, HEX); 
  Serial.print("Firmware ver. "); Serial.print((versiondata>>16) & 0xFF, DEC); 
  Serial.print('.'); Serial.println((versiondata>>8) & 0xFF, DEC);
  
  // configure board to read RFID tags
  nfc.SAMConfig();
  
  /*SMARTGUN SETUP*/

  smartGun.setFlags(REG | AWAKE); //for now, assume that the device is owned by the user and that it is awake on startup

  /*DEMO SETUP STUFF*/
  //for use with Arduino Mega 2560
  pinMode(FIRE_BUTTON, OUTPUT); //LED response to button and NFC tag
  pinMode(MODE, INPUT); //LED for indicating mode of operation
  pinMode(53, OUTPUT);

  digitalWrite(FIRE_BUTTON, LOW); //by default, fire button is not active
  
}

void loop(void) {
  
  uint8_t success;
  uint8_t uid[] = { 0, 0, 0, 0, 0, 0, 0 };  // Buffer to store the returned UID
  uint8_t uidLength;                        // Length of the UID (4 or 7 bytes depending on ISO14443A card type)
    
  // Wait for an NTAG203 card.  When one is found 'uid' will be populated with
  // the UID, and uidLength will indicate the size of the UUID (normally 7)

  Serial.println("Waiting for an ISO14443A Card ...");
  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);

  if(digitalRead(MODE) == LOW) { //then we are not in wifi mode
    Serial.println("FIRING MODE ACTIVE");
    
    //add nfc tag to database
    if (recordId < ENTRY_COUNT) {
      appendEntry(recordId, nameGen(recordId), uid);
      Serial.println((smartGun.db)->count());
      recordId++;
     }
    dbCount(); 
    dbPrint();
    Serial.println("DONE");
        
    if (success) {
      // Display some basic information about the card
      Serial.println("Found an ISO14443A card");
      Serial.print("  UID Length: ");Serial.print(uidLength, DEC);Serial.println(" bytes");
      Serial.print("  UID Value: ");
      nfc.PrintHex(uid, uidLength);
      Serial.println("");
      
      if (uidLength == 7)
      {
        //search db for tag here
        tagSearch(uid);
        //ready gun to fire if authorization has been approved
        smartGun.getFlags() & AUTH ? digitalWrite(FIRE_BUTTON, HIGH): digitalWrite(FIRE_BUTTON, LOW);
        
        uint8_t data[32];
        
        // We probably have an NTAG2xx card (though it could be Ultralight as well)
        Serial.println("Seems to be an NTAG2xx tag (7 byte UID)");         
  
        for (uint8_t i = 0; i < 42; i++) 
        {
          success = nfc.ntag2xx_ReadPage(i, data);
          
          // Display the current page number
          Serial.print("PAGE ");
          if (i < 10)
          {
            Serial.print("0");
            Serial.print(i);
          }
          else
          {
            Serial.print(i);
          }
          Serial.print(": ");
  
          // Display the results, depending on 'success'
          if (success) 
          {
            // Dump the page data
            nfc.PrintHexChar(data, 4);
          }
          else
          {
            Serial.println("Unable to read the requested page!");
            //if vision of tag is lost, then we disconnect fire mechanism 
            digitalWrite(FIRE_BUTTON, LOW);
            break;
          }
        }     
      
      }
      else
      {
        Serial.println("This doesn't seem to be an NTAG203 tag (UUID length != 7 bytes)!");
      }
      
      // Wait a bit before trying again
  //    Serial.println("\n\nSend a character to scan another tag!");
  //    Serial.flush();
  //    while (!Serial.available()); //what causes the script to pause for manual input, will need to make this automatic
  //    while (Serial.available()) {
  //    Serial.read();
  //    }
      Serial.flush(); 
        
    }
  } else {/*TODO: need to update flags for smart gun object based on if wifi is established*/
      
      Serial.println("WIFI MODE ACTIVE");

      // check for the presence of the shield:
      if (WiFi.status() == WL_NO_SHIELD) {
        //Serial.println("WiFi shield not present");
        // don't continue:
        while (true);
      }
      Serial.println("TEST 1");
    
      // attempt to connect to WiFi network:
      while (status != WL_CONNECTED) {
        Serial.print("Attempting to connect to SSID: ");
        Serial.println(ssid);
        // Connect to WPA/WPA2 network. Change this line if using open or WEP network:
        status = WiFi.begin(ssid, pass);
        Serial.println("Test 2");
    
        // wait 10 seconds for connection:
        delay(10000);
      }
      Serial.println("Connected to wifi");
      printWiFiStatus();
    
      Serial.println("\nStarting connection to server...");
      // if you get a connection, report back via serial:
      z = client.connect(server,9999);
      Serial.println("our result from connect is");
      unsigned int nick = 10;
      char nah = 'A';
      Serial.println(z);
      if (z) {
        Serial.println("connected to server");
        // Make a HTTP request:
        client.println("cedric");
        client.println("GET /search?q=arduino HTTP/1.1");
        client.println("Host: www.google.com");
        client.println("Connection: close");
        client.println("n");
        client.println("CLEARLY");
        client.println("/n");
        client.println(nick);
        client.println(nah);
        client.println("vineet");
      }
  
  
      // if there are incoming bytes available
      // from the server, read them and print them:
      while (client.available()) {
        char c = client.read();
        Serial.write(c);
      }
      
      // if the server's disconnected, stop the client:
      if (!client.connected()) {
        Serial.println();
        Serial.println("disconnecting from server.");
        client.stop();
      
    }
    

  }
}

//custom functions

//gives max number of entries allowed
void dbLimit() {
  Serial.print("Database Limit: ");
  Serial.println((smartGun.db)->limit());
}

//gives the current number of entries in the database
int dbCount() {
  Serial.print("Database count: ");
  Serial.println((smartGun.db)->count());
  return (smartGun.db)->count();
}

void dbPrint() {
  Serial.println("Printing database");
  for(int i = 1; i <= (smartGun.db)->count(); ++i) {
    EDB_Status result = (smartGun.db)->readRec(i, EDB_REC entry); //EDB_REC is the struct instance of an entry in the table
      if (result == EDB_OK) {
        Serial.println("id: ");
        Serial.println(entry.id);
        Serial.println("name: ");
        Serial.println(entry.userName);
        Serial.println("tag: ");
        for(int j = 0; j < 7; ++j) {
          Serial.print(entry.nfcTag[j]);
          if(j != 6) Serial.print(":");
        }
        Serial.println();
      }
      else printError(result);
  }
}

void appendEntry(int id, char* userName, uint8_t* nfcTag)
{
  Serial.print("Appending record...");
  entry.id = id; 
  entry.userName = userName;
  entry.nfcTag = nfcTag;
  EDB_Status result = (smartGun.db)->appendRec(EDB_REC entry);
  if (result != EDB_OK) printError(result);
  Serial.println("DONE");
}

void deleteAll()
{
  Serial.print("Truncating table...");
  (smartGun.db)->clear();
  Serial.println("DONE");
}

void deleteEntry(int recno)
{
  Serial.print("Deleting recno: ");
  Serial.println(recno);
  (smartGun.db)->deleteRec(recno);
}

void tagSearch(uint8_t* uid) {
  for (int recno = 1; recno <= (smartGun.db)->count(); recno++)
  {
    EDB_Status result = (smartGun.db)->readRec(recno, EDB_REC entry);
    if (result == EDB_OK)
    {
      if (entry.nfcTag == uid) {
        Serial.println("ID success!");
        smartGun.setFlags(AUTH); //set authorization
        return;
      }
    }
    else printError(result);
  }

  Serial.println("ID not found!");
  smartGun.resetFlags(AUTH); //remove authorization
}

/*WIFI HELPER FUNCTION*/
void printWiFiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}

void printError(EDB_Status err)
{
  Serial.print("ERROR: ");
  switch (err)
  {
    case EDB_OUT_OF_RANGE:
      Serial.println("Recno out of range");
      break;
    case EDB_TABLE_FULL:
      Serial.println("Table full");
      break;
    case EDB_OK:
    default:
      Serial.println("OK");
      break;
  }
}

/* EXAMPLE FUNCTION FOR SIMULATION */
//takes in 1 arguement, the number of entries to create
char* nameGen(int id) {
  dbLimit();
  randomSeed(analogRead(0));
  char* nameSim;
  
  switch(id) {
    case 1 : nameSim = "BOB";
             break;
    case 2 : nameSim = "AMAN";
             break;
    case 3 : nameSim = "SUSAN";
             break;
    case 4 : nameSim = "DEQUAN";
             break;
    case 5 : nameSim = "LEE MIN HO";
             break;
    default : nameSim = "NO FACE";
  }

  Serial.println(nameSim);
  return nameSim;
}
