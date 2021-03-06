//class for the smart gun device

/* NOTES

use EDB::open to read from existing database
if this funcion does not return EDB_ok, then the database does not exist and we need to create a new one

ALL of these functions need to be implemented in arduino
	Flag wakeUp(); //will wake up on nfc tag detection
	void connect(); //attempt to connect via bluetooth. triggered by external button? set networkFlag to 1 on success
	void disconnect(); //if networkFlag is 1, attempt to disconnect
	void authorize(uint8_t nfcTag[7]); //read nfc id, sets authFlag if this nfc id is in the smartgun's database
	void ledSet(); //sets connected LED's based on flag values
	void sendFlags(); // sends info of flags to web app for monitoring


EDB_Rec is a byte*, so anything of this type is a pointer to bytes
*/
#include "Arduino.h"
#include <EDB.h>

#pragma once

class SGD {

	public:
		//pulled from EDB code
		typedef void EDB_Write_Handler(unsigned long, const uint8_t);
    	typedef uint8_t EDB_Read_Handler(unsigned long);
    	
		//variable
		EDB* db; //database instance

		//functions
		SGD(EDB_Write_Handler *, EDB_Read_Handler *); //should create an ID for the gun on instance creation
		~SGD();
		uint8_t getFlags();
		void setFlags(uint8_t mask); //set flags using bitwise OR
		void resetFlags(uint8_t mask); //reset flags using bitwise AND

	private:
		/* the status flag from left to right is as follows:
		bit0: indicates the device is currently registered to a user (0x80)
		bit1: indicates that the gun is awake (0x40)
		bit2: indicates the gun is connected to the web app (0x20)
		bit3: indicates the gun has authorized a tag and is ready for use (0x10)
		bits 4 - 8: not used, yet
		*/
		uint8_t statusFlags = 0x00;
		char* sgdId; //id used in first time authentication, will deallocate the id once checked by webapp

    
};