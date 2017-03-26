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
#include <avr/wdt.h>

#define TABLE_SIZE 4096 //this size is for the mega
#define ENTRY_COUNT 10
#define DB_START 0 //the adress in which the database starts

#define FIRE_BUTTON 25
#define MODE 23

//for wifi
#define MEGA_CS 44
#define MEGA_IRQ 21
#define MEGA_RST 46
#define MEGA_WAKE 41
#define PORT 10000

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
  //NOTE: if you want to upload a new script to the arduino, you should reset the db manually by using the code below
//  deleteAll(); //for testing
//  (smartGun.db)->create(DB_START, TABLE_SIZE, (unsigned int)sizeof(entry)); //if we want to reset the database
  // create table at with starting address 0
  if((smartGun.db)->open(DB_START) != EDB_OK) { 
    Serial.println("Database does not exist on this device");
    Serial.println("Creating database");
    (smartGun.db)->create(DB_START, TABLE_SIZE, (unsigned int)sizeof(entry));
  } else {
    Serial.println("Using Stored Database");
  }
  Serial.println("DONE");

  /*WIFI SETUP*/
  WiFi.setPins(MEGA_CS,MEGA_IRQ,MEGA_RST);

  
  nfc.begin();

  uint32_t versiondata = nfc.getFirmwareVersion();
  
  if (! versiondata) {
    Serial.print("Didn't find PN53x board");
    while (1); // halt
  }
  Serial.println("TEST 1");
  
  // Got ok data, print it out!
  Serial.print("Found chip PN5"); Serial.println((versiondata>>24) & 0xFF, HEX); 
  Serial.print("Firmware ver. "); Serial.print((versiondata>>16) & 0xFF, DEC); 
  Serial.print('.'); Serial.println((versiondata>>8) & 0xFF, DEC);
  
  // configure board to read RFID tags
  nfc.SAMConfig();
  
  /*SMARTGUN SETUP*/
  smartGun.setFlags(AWAKE); //for now, assume that the device is owned by the user and that it is awake on startup

  /*WATCHDOG SETUP*/
  wdt_disable(); //always good to disable it, if it was left 'on' or you need init time

  /*DEMO SETUP STUFF*/
  //for use with Arduino Mega 2560
  pinMode(FIRE_BUTTON, OUTPUT); //LED response to button and NFC tag
  pinMode(MODE, INPUT); //LED for indicating mode of operation
  pinMode(MEGA_WAKE, OUTPUT);
  pinMode(53, OUTPUT);

  digitalWrite(FIRE_BUTTON, LOW); //by default, fire button is not active
  digitalWrite(MEGA_WAKE, LOW); //only enable wifi if wifi swich is active
  
}

void loop(void) {
  char newUsrNm[16];
  uint8_t success;
  uint8_t uid[] = { 0, 0, 0, 0, 0, 0, 0 };  // Buffer to store the returned UID
  uint8_t uidLength;                        // Length of the UID (4 or 7 bytes depending on ISO14443A card type)
  smartGun.setFlags(REG);
    
  // Wait for an NTAG203 card.  When one is found 'uid' will be populated with
  // the UID, and uidLength will indicate the size of the UUID (normally 7)

  Serial.println("Waiting for an ISO14443A Card ...");
  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);

  if(digitalRead(MODE) == LOW) { //then we are not in wifi mode
    Serial.println("FIRING MODE ACTIVE");
        
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
        dbPrint();
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
      
      Serial.flush(); 
        
    }
  } else {/*TODO: need to update flags for smart gun object based on if wifi is established*/
      digitalWrite(MEGA_WAKE, HIGH);

      Serial.println("WIFI MODE ACTIVE");
      Serial.println("DELETING DATABASE for testing adding tag req");
      deleteAll();
      
//      //add nfc tag to database (for testing)
//      if ((smartGun.db)->count() < ENTRY_COUNT) {
//        appendEntry((smartGun.db)->count()+1, nameGen((smartGun.db)->count()+1), uid);
//        Serial.println((smartGun.db)->count());
//       }
//      dbCount(); 
//      dbPrint();
      Serial.println("DONE");

      // check for the presence of the shield:
      if (WiFi.status() == WL_NO_SHIELD) {
        Serial.println("WiFi shield not present");
        // don't continue:
        while (true);
      }
    
      // attempt to connect to WiFi network:
      while (status != WL_CONNECTED) {
        Serial.print("Attempting to connect to SSID: ");
        Serial.println(ssid);
        // Connect to WPA/WPA2 network. Change this line if using open or WEP network:
        status = WiFi.begin(ssid, pass);
    
        // wait 10 seconds for connection:
        delay(10000);
      }
      Serial.println("Connected to wifi");
      printWiFiStatus();
    
      Serial.println("\nStarting connection to server...");
      // if you get a connection, report back via serial:
      
      //sendDb(); //send the database info to the web app

      //TODO: database not retaining username on subsequent calls when we try to get name from web app
      if(tagSearch(uid) == 0) { //if tag does not exist in db
         Serial.println("New tag found! req to add from web app");
         if(sendNewTagReq(newUsrNm) == 1) { //if usrnm was given by webapp
            if ((smartGun.db)->count() < ENTRY_COUNT) {
              appendEntry((smartGun.db)->count()+1, newUsrNm, uid);
              Serial.println((smartGun.db)->count());
            } else {
              Serial.println("NOT ENOUGH SPACE IN DATABASE");
            }
         }
      }
      
      // if the server's disconnected, stop the client:
      if (!client.connected()) {
        Serial.println();
        Serial.println("disconnecting from server.");
        client.stop();
      
      }

    digitalWrite(MEGA_WAKE, LOW);

    if ((smartGun.db)->count() >= ENTRY_COUNT) {
      Serial.println("DB limit reached, resetting db");
      deleteAll();
    }
    
    Serial.flush();
    sysRestart(); //restart the system
    
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

uint8_t tagSearch(uint8_t* uid) {
  for (int recno = 1; recno <= (smartGun.db)->count(); recno++)
  {
    EDB_Status result = (smartGun.db)->readRec(recno, EDB_REC entry);
    if (result == EDB_OK)
    {
      if (entry.nfcTag == uid) {
        Serial.println("ID success!");
        smartGun.setFlags(AUTH); //set authorization
        return 1;
      }
    }
    else printError(result);
  }

  Serial.println("ID not found!");
  smartGun.resetFlags(AUTH); //remove authorization
  return 0;
}


void sendDb() {
  z = client.connect(server,PORT);
  Serial.println("our result from connect is");
  Serial.println(z);
  if (z) { //nfc craps out when we try to send information
    Serial.println("connected to server");
    client.println(smartGun.getSgdId());

    for(int i = 1; i <= (smartGun.db)->count(); i++) {
      EDB_Status result = (smartGun.db)->readRec(i, EDB_REC entry);
      if (result == EDB_OK){
        client.print(entry.id);
        client.print(" ");
        client.print(entry.userName);
        client.print(" ");
        for(int j = 0; j < 7; ++j) {
          client.print(entry.nfcTag[j]);
          if(j != 6) client.print(":");
        }

        client.print("\r\n"); //parsing token
      } else {
        Serial.println("failed to recieve db entry");
        return;
      }
    }
    
    client.println("SGD:END"); //ending token
  } else {
    Serial.println("error in client connection");
  }
}

uint8_t sendNewTagReq(char* newUsrNm) {
  int i = 0;
  z = client.connect(server,PORT);
  Serial.println("our result from connect is");
  Serial.println(z);
  if(z) {
    Serial.println("connected to server");
    client.print("NEW");
  } else {
    Serial.println("error in client connection");
    return 0;
  }
  //will need to read info given from user
  // if there are incoming bytes available
  // from the server, read them and print them:
  Serial.println("the user name is...");
  while(!client.available()); //wait for info to be availible
  while (client.available()) {
    newUsrNm[i] = client.read();
    if(newUsrNm[i] == '\0') {
      return 1;
    }
    i++;
    Serial.print(newUsrNm[i]);
    if (i >= 15) {
      newUsrNm[15] = '\0';
    }
  }
  return 1;
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

//watchdog reset function
void wdt_delay(unsigned long msec) {
  wdt_reset();
  
  while(msec > 1000) {
    wdt_reset();
    delay(1000);
    msec -= 1000;
  }
  delay(msec);
  wdt_reset();
}

//forced restart function
void sysRestart() {
  wdt_enable(WDTO_1S); //endable wtd to 1s, and wait 1 sec for sys retart
  delay(1001);
}

/*for debugging*/

// this function will return the number of bytes currently free in RAM      
extern int  __bss_end; 
extern int  *__brkval; 
int freemem()
{ 
int free_memory; 
if((int)__brkval == 0) 
   free_memory = ((int)&free_memory) - ((int)&__bss_end); 
else 
   free_memory = ((int)&free_memory) - ((int)__brkval); 
return free_memory; 
}
