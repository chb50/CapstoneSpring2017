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

void SGD::setFlags(uint8_t mask) {
	statusFlags = statusFlags || mask;
	return;
}

void SGD::resetFlags(uint8_t mask) {
	statusFlags = statusFlags & mask;
	return;
}

