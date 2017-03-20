#include "smartgun.h"
#include "Arduino.h"
#include <stdio.h>
#include <stdlib.h>     /* srand, rand */
#include <time.h>       /* time */
#include <EDB.h>


SGD::SGD(EDB_Write_Handler *w, EDB_Read_Handler *r) {
	//generate random id to upload
	sgdId = new char[16];
	srand(time(NULL));
	//every smart gun device starts with "SGD:"
	sgdId[0] = 'S'; sgdId[1] = 'G'; sgdId[2] = 'D'; sgdId[3] = ':';
	for(int i = 4; i < 16; ++i) {
		int randNum = rand() % 26;
		sgdId[i] = 'A' + randNum; //incriment ascii by "randNum" to get random capital letter
	}

	//initialize database
	db = new EDB(w,r);

}

SGD::~SGD() {
	delete sgdId;
	delete db;
}

uint8_t SGD::getFlags() {
	return statusFlags;
}

void SGD::setFlags(SGD_Status status) {
	statusFlags = statusFlags | status;
	return;
}

void SGD::resetFlags(SGD_Status status) {
	statusFlags = statusFlags & (!status); //removes inidcated flag while leaving other flags untouched (flips bits to 1 instead of flag, which is flipped to 0)
	return;
}

/* This function was derived from the edbRead function in the EDB library
* This function is intended to get a record from the database and convert said record into a string to be passed
* to the web app over wifi connection. HOWEVER, I do not know the type of each member that I am extracting
* from the database. Common sense would say that it should be the same as the type of each member variable declared
* within the struct used to store the records, but I dont know if the EDB class preserves type when storing on EEPROM
* Will need to do some testing on the Wifi module with the web app to confirm this
*/
char* SGD::getDBData(unsigned long recno, EDB_Rec rec) {
  if (recno < 1 || recno > db->EDB_head.n_recs) {
  	char* err = "OUT OF RANGE";
  	return err;
  }
  db->edbRead(db->EDB_table_ptr + ((recno - 1) * db->EDB_head.rec_size), rec, db->EDB_head.rec_size);

  //package it into a buffer
  char buff[db->EDB_head.rec_size];
  for(int i = 0; i < db->EDB_head.rec_size; i++) {
  	buff[i] = *rec; //we will need to test. dont know if the member type holds when each entry stores its members into the database
  	rec++;
  }

  return buff;
}

/* Private Functions */

void uint8ToChar(uint8_t num, char* buff) {
	uint8_t numcpy = num;
	uint8_t i = 0;

	while(numcpy >= 100) {
		i++;
		numcpy -= 100;
	}

	buff[0] = i + 48; //"48" is the character '0' in ascii
	i = 0; //reset i

	while(numcpy >= 10) {
		i++;
		numcpy -= 10;
	}

	buff[1] = i + 48;
	buff[2] = numcpy + 48;
	buff[3] = '\0';

	return;
 }

