#include "Arduino.h"
#include <smartgun.h>
#include <EEPROM.h>

#define TABLE_SIZE 1024
#define ENTRY_COUNT 10

struct entry {
  //800 bytes for 10 entries
  uint8_t id;
  char* userName;
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



void setup() {
  
  Serial.begin(9600);
  Serial.println("Extended Database Library + Arduino Internal EEPROM Demo");
  Serial.println();

  randomSeed(analogRead(0));
  
  Serial.print("Creating table...");
  // create table at with starting address 0
  (smartGun.db)->create(0, TABLE_SIZE, sizeof(entry));
  Serial.println("DONE");

}

void loop() {
  // put your main code here, to run repeatedly:

}

//custom functions

//gives max number of entries allowed
void dbLimit() {
  Serial.print("(smartGun.db) Limit: ");
  Serial.println((smartGun.db)->limit());
}

//gives the current number of entries in the database
void dbCount() {
  Serial.print("(smartGun.db) count: ");
  Serial.println((smartGun.db)->count());
}

void dbPrint() {
  for(int i = 0; i < (smartGun.db)->count(); ++i) {
    EDB_Status result = (smartGun.db)->readRec(i, EDB_REC entry); //E(smartGun.db)_REC is the struct instance of an entry in the table
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
