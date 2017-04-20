/* WRITTEN BY: Cedric Blake
 *  
 *  This script uses external libraries libraries:
 *  
 *  SGD
 *  EDB
 *  Adafruit pn532 (nfc library)
 *  
 *  will need to download these if you want script to work
 */


/* DEBUGGING NOTES
 *  
 *  make sure to not use too many serial print statements, as they take space in ram and may lead to unexpected results in code
 */

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
#include <EDB.h>
#include <EEPROM.h>
#include <assert.h>
#include <Wire.h>
#include <SPI.h>
#include <WiFi101.h>
#include <Adafruit_PN532.h>
#include <avr/wdt.h>
#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif

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

//for nfc
#define T_OUT_1 1000
#define T_OUT_5 5000

//for leds
/*NOTE: led color states:
 * red flashing - waiting for nfc tag
 * red freeze - found a tag, but not authorized to shoot
 * green freeze - found a tag, authorized to shoot
 * yellow freeze - attempting to connect to wifi
 * blue freeze - wifi connection established
 */
#define LED_STATE 27
#define NUM_LEDS 8
#define BRIGHTNESS 50
#define SNAKE_SIZE 4

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

// Create an SGD and EDB object
SGD smartGun;
EDB db(&writer, &reader);

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

//char ssid[] = "CB6SC"; //  your network SSID (name)
//char pass[] = "YWXYGTR36XGSJBY6";

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

//led object
Adafruit_NeoPixel strip = Adafruit_NeoPixel(NUM_LEDS, LED_STATE, NEO_KHZ800 + NEO_RGB);

void setup(void) {
  Serial.begin(9600);
  while (!Serial);
  Serial.println("Hello!");

//  Serial.print("Smart gun ID: ");
//  Serial.println(smartGun.getSgdId());

  randomSeed(analogRead(0));
  //NOTE: if you want to upload a new script to the arduino, you should reset the db manually by using the code below
//  deleteAll(); //for testing
//  db.create(DB_START, TABLE_SIZE, (unsigned int)sizeof(entry)); //if we want to reset the database
  // create table at with starting address 0
  if(db.open(DB_START) != EDB_OK) { 
    Serial.println("Database does not exist on this device");
    Serial.println("Creating database");
    db.create(DB_START, TABLE_SIZE, (unsigned int)sizeof(entry));
  } else {
    Serial.println("Using Stored Database");
  }

  /*WIFI SETUP*/
  WiFi.setPins(MEGA_CS,MEGA_IRQ,MEGA_RST);

  
  nfc.begin();

  uint32_t versiondata = nfc.getFirmwareVersion();
  
  if (! versiondata) {
    Serial.print("Didn't find PN53x board");
    while (1); // halt
  }
  
  // Got ok data, print it out!
  Serial.print("Found chip PN5\n");
  
  // configure board to read RFID tags
  nfc.SAMConfig();
  
  /*SMARTGUN SETUP*/
  smartGun.setFlags(AWAKE); //for now, assume that the device is owned by the user and that it is awake on startup
  smartGun.resetFlags(WIFI_CONN); //not connected to wifi yet

  /*LED SETUP*/
  #if defined (__AVR_ATtiny85__)
    if (F_CPU == 16000000) clock_prescale_set(clock_div_1);
  #endif
  Serial.begin(9600);
  strip.setBrightness(BRIGHTNESS);
  strip.begin();
  strip.show(); // Initialize all pixels to 'off'

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

  //NOTE: need this print to store and hold the username on the database
  //WATCH OUT FOR THIS, it may give bugs if we try to add multiple tags
  //Serial.print(newUsrNm);
//  Serial.println("\nTime to change mode!");
//  delay(5000);

  if(digitalRead(MODE) == LOW) { //then we are not in wifi mode
    
    Serial.println("FIRING MODE ACTIVE");
    stateSnake(SNAKE_SIZE, 255, 0, 0, false); //set leds to red, ocillate

    wdt_enable(WDTO_2S);
    Serial.println("\nWaiting for an ISO14443A Card ...");
    success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength, T_OUT_1);
    wdt_reset(); 
        
    if (success) {
      // Display some basic information about the card
      Serial.println("Found an ISO14443A card");
      nfc.PrintHex(uid, uidLength);
      Serial.println("");
      
      if (uidLength == 7)
      {
        //search db for tag here
//        //add nfc tag to database (for testing)
        //NOTE: the simulation is able to retain info even after system shutdown. may wanna try dealing with the name problem first
//        if (db.count() < ENTRY_COUNT) {
//          appendEntry(db.count()+1, nameGen(db.count()+1), uid);
//          Serial.println(db.count());
//         }
        dbCount();
        dbPrint();
        
        //set authorization
        if(tagSearch(uid)) {
          smartGun.setFlags(AUTH);
          stateSnake(SNAKE_SIZE, 0, 255, 0, true); //led set to green, freeze
        } else {
          smartGun.resetFlags(AUTH);
          stateSnake(SNAKE_SIZE, 255, 0, 0, true); //led set to red, freeze
        }
        //ready gun to fire if authorization has been approved
        smartGun.getFlags() & AUTH ? digitalWrite(FIRE_BUTTON, HIGH): digitalWrite(FIRE_BUTTON, LOW);
        
        uint8_t data[32];
  
        for (uint8_t i = 0; i < 42; i++) 
        {
          success = nfc.ntag2xx_ReadPage(i, data);
  
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
  } else {
      digitalWrite(MEGA_WAKE, HIGH);
      wdt_disable();//if we come from firing mode
      Serial.println("WIFI MODE ACTIVE");
      stateSnake(SNAKE_SIZE, 255, 255, 0, false);//set leds to yellow, ocillate
      //deleteAll();
      
//      //add nfc tag to database (for testing)
//      //DONT FORGET TO DELETE ALL IF DB IS FULL WHEN DOING SIMULATION
//      if (db.count() < ENTRY_COUNT) {
//        appendEntry(db.count()+1, nameGen(db.count()+1), uid);
//        Serial.println(db.count());
//       }

      // check for the presence of the shield:
      if (WiFi.status() == WL_NO_SHIELD) {
        Serial.println("WiFi shield not present");
        // don't continue:
        while (true);
      }
    
      // attempt to connect to WiFi network:
      while (status != WL_CONNECTED) {
        Serial.print("Attempting to connect to SSID: ");
        stateSnake(SNAKE_SIZE, 255, 255, 0, true);//set leds to yellow, flash on every loop
        Serial.println(ssid);
        // Connect to WPA/WPA2 network. Change this line if using open or WEP network:
        status = WiFi.begin(ssid, pass);
    
        // wait 10 seconds for connection:
        delay(10000);
        led_reset();
      }
      //printWiFiStatus();
    
      Serial.println("\nStarting connection to server...");
      // if you get a connection, report back via serial:
      led_reset();
      stateSnake(SNAKE_SIZE, 255, 255, 0, true);//set leds to yellow, flash on every loop
      z = client.connect(server,PORT);
      if(z) {
        smartGun.setFlags(WIFI_CONN);
      } else {
        Serial.println("error in client connection");
        return 0;
      }

      stateSnake(SNAKE_SIZE, 0, 0, 255, true);//set leds to blue, freeze

      reqHandle(newUsrNm, uid, uidLength);
      
      // if the server's disconnected, stop the client:
      if (!client.connected()) {
        Serial.println();
        Serial.println("disconnecting from server.");
        smartGun.resetFlags(WIFI_CONN);
        client.stop();
      
      }

    digitalWrite(MEGA_WAKE, LOW);

    //to be used with testing when manually adding entries
    if (db.count() >= ENTRY_COUNT) {
      Serial.println("DB limit reached, resetting db");
      deleteAll();
    }
    
    Serial.flush();
    //sysRestart(); //restart the system, use if wifi back to nfc is giving you trouble
  }
}

//custom functions

//gives max number of entries allowed
void dbLimit() {
  Serial.print("Database Limit: ");
  Serial.println(db.limit());
}

//gives the current number of entries in the database
int dbCount() {
  Serial.print("Database count: ");
  Serial.println(db.count());
  return db.count();
}

//print the database
void dbPrint() {
  Serial.println("Printing database");
  for(int i = 1; i <= db.count(); ++i) {
    EDB_Status result = db.readRec(i, EDB_REC entry); //EDB_REC is the struct instance of an entry in the table
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

//add and entry to the database
void appendEntry(int id, char* userName, uint8_t* nfcTag) {
  Serial.print("Appending record...");
  entry.id = id;
  entry.userName = new char[16];
  for(int i = 0; i < strlen(userName)+1; i++) {
    if(i < 16) { //make sure string is smaller than 16 bytes
      entry.userName[i] = userName[i];
    } else {
      entry.userName[16] = '\0';
      break;
    }
  }
  entry.nfcTag = new uint8_t[7];
  for(int i = 0; i < 7; i++) {
    entry.nfcTag[i] = nfcTag[i];
  }
  EDB_Status result = db.appendRec(EDB_REC entry);
  if (result != EDB_OK) printError(result);
}

//delete all entries in the database
void deleteAll() {
  Serial.print("Truncating table...");
  for(int i = 1; i <= db.count(); ++i) {
    EDB_Status result = db.readRec(i, EDB_REC entry); //EDB_REC is the struct instance of an entry in the table
    if (result == EDB_OK) {
      delete entry.userName;
      delete entry.nfcTag;
    }
    else printError(result);
  }
  db.clear();
}

//delete an entry of the database
void deleteEntry(int recno) {
  Serial.print("Deleting recno");
  EDB_Status result = db.readRec(recno, EDB_REC entry); //EDB_REC is the struct instance of an entry in the table
  if (result == EDB_OK) {
    delete entry.userName;
    delete entry.nfcTag;
  }
  else printError(result);
  db.deleteRec(recno);
}

//search through database based on tag id
uint8_t tagSearch(uint8_t* uid) {
  for (int recno = 1; recno <= db.count(); recno++)
  {
    EDB_Status result = db.readRec(recno, EDB_REC entry);
    if (result == EDB_OK)
    {
      int match = 1;
      for(int i = 1; i <= db.count(); ++i) {
        if(entry.nfcTag[i] != uid[i]) {
          match = 0;
          break;
        }
      }
      if(match) {
        Serial.println("ID Found!");
        return 1;
      }
    }
    else printError(result);
  }
  Serial.println("ID not found!");
  return 0;
}

//search through database by user name
uint8_t nameSearch(char* userName) {
  for (int recno = 1; recno <= db.count(); recno++)
  {
    EDB_Status result = db.readRec(recno, EDB_REC entry);
    if (result == EDB_OK)
    {
      int match = 1;
      strcmp(entry.userName, userName);
      
      if(match) {
        Serial.println("Name Found!");
        return 1;
      }
    }
    else printError(result);
  }
  Serial.println("Name not found!");
  return 0;
}

//send unique smartgun id to web app
void sendId() {
  if(smartGun.getFlags() & WIFI_CONN){
    Serial.println("Sending ID");
    client.println(smartGun.getSgdId());
  } else {
    Serial.println("Failed to retrieve id");
  }
}

//send db contents to web app
void sendDb() {
  if (smartGun.getFlags() & WIFI_CONN) { //nfc craps out when we try to send information
    Serial.println("Sending DB info");
    client.println("SGD:"); // starting token
    
    for(int i = 1; i <= db.count(); i++) {
      EDB_Status result = db.readRec(i, EDB_REC entry);
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
    
  } else {
    Serial.println("error in client connection");
  }
}

//get a username sent from the web app
uint8_t getNewTagName(char* newUsrNm) {
  //wdt_enable(WDTO_8S); //watchdog set to 8 sec for infinite loop in this function
  if(smartGun.getFlags() & WIFI_CONN) { //check to see if we connected to the webapp
    int i = 0;
    
    //will need to read info given from user
    // if there are incoming bytes available
    // from the server, read them and print them:
    Serial.println("Recieving username...");
//    while(!client.available()); //vineet is sending as 1 string, so i dont think we need this
//    wdt_reset(); //reset wd so system doesnt restart
    do {
      newUsrNm[i] = client.read();
      i++;
      if (!client.available() or i == 15) {
        newUsrNm[i] = '\0';
      }
    }while (client.available() and newUsrNm[i] != '\0');
//    wdt_disable();
    client.print("NAME_GET");
    Serial.println(newUsrNm);
    return 1;
  } else {
    Serial.println("Smartgun not connected!");
    wdt_disable();
    return 0;
  }
}

//read in a tag for adding a new user to the database
void readNewTag(char* newUsrNm, uint8_t* uid, uint8_t uidLength) {
  uint8_t success;
  int timeout = 0;
  wdt_enable(WDTO_8S); //hardware a bit buggy here, so we adding this
  Serial.println("Waiting for an ISO14443A Card ...");
  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength, T_OUT_5);
  while(!success) {
    wdt_reset();
    timeout++;
      if(timeout >= 6) { //wait 5*6 = 30 sec for user to place tag
        Serial.println("Timeout occured on adding tag!");
        //should probably send something to the server here about the time out
        return;
      }
    success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength, T_OUT_5);
  }
  wdt_disable();
  //search through database to see if tag is already in there
  if(!tagSearch(uid)) {
    Serial.println("adding tag!");
    if (db.count() < ENTRY_COUNT) {
      appendEntry(db.count()+1, newUsrNm, uid);
    } else {
      Serial.println("NOT ENOUGH SPACE IN DATABASE");
      return;
    }
  } else {
    Serial.println("Tag already exists!");
    return;
  }
}

//recieves request from database about which data to send
void reqHandle(char* newUsrNm, uint8_t* uid, uint8_t uidLength) {
//  wdt_enable(WDTO_8S); //adds redundancy for safety, if regular timeout fails, then reset system
  Serial.println("waiting for request");
  while(!client.available()) { //wait for server to send a request
    if(!digitalRead(MODE)) {
      return;
    }
  }
//  wdt_disable();

  char c = client.read();
  Serial.println("REQUEST FROM WEB APP: ");
  Serial.println(c);
  switch (c) {
    case 'O': //ID req
      sendId();
      break;
    case 'D': //DB req
      sendDb();
      break;
    case 'N': //Add Tag req
      Serial.println("N request get!");
      if(!getNewTagName(newUsrNm)) {
        Serial.println("ERROR IN AQUIRING USERNAME");
        return;
      }
      client.stop(); //need to do this in order to run nfc tag
      readNewTag(newUsrNm, uid, uidLength);
      break;
    case 'R': //Remove Tag req
      Serial.println("REMOVE USER NAME REQ");
      if(!getNewTagName(newUsrNm)) {
        Serial.println("ERROR IN AQUIRING USERNAME");
        return;
      }
      Serial.print("Tag name Request: ");
      Serial.println(newUsrNm);
      deleteEntry(nameSearch(newUsrNm));
      break;
    case 'L': //Log out notice
      Serial.println("LOG OUT");
      client.stop(); //user has logged out
      break;
    default:
      Serial.println("INVALID REQUEST");
      break;
  }
}

//db error handling function
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

//led function, displays state of gun
//for now, assume 255 passed in for rgb
void stateSnake(uint8_t sSize, uint8_t red, uint8_t green, uint8_t blue, bool freeze) {
  uint8_t snakeSize = sSize;
  int snakeHead = NUM_LEDS - 1;
  while (snakeHead + snakeSize >= 0) {
    if(freeze == false) { //this pauses the led output
      for(int i = 0; i < NUM_LEDS; i++) {
        strip.setPixelColor(i, strip.Color(0,0,0));
      }
      strip.show();
    }
    uint8_t r = red; uint8_t g = green; uint8_t b = blue;
    for(int i = snakeHead; i < snakeHead + snakeSize; i++) {
      if(i >= snakeHead and i < snakeHead + snakeSize) {
        strip.setPixelColor(i, strip.Color(green, red, blue));
      } 
    }
    strip.show();
    delay(50);
    snakeHead--;
  }
}

//turn off all leds, can be used for blinking effect
void led_reset() {
  for(int i = 0; i < NUM_LEDS; i++) {
    strip.setPixelColor(i, strip.Color(0,0,0));
  }
  strip.show();
  delay(100);
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

//forced restart function
void sysRestart() {
  wdt_enable(WDTO_1S); //endable wtd to 1s, and wait 1 sec for sys retart
  delay(1001);
}
