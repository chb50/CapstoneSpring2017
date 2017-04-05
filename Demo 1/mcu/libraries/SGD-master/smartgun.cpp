#include "smartgun.h"
#include "Arduino.h"
#include <stdio.h>
#include <stdlib.h>     /* srand, rand */
#include <time.h>       /* time */
#include <EDB.h>


SGD::SGD() {
	//generate random id to upload
	sgdId = new char[16];
	srand(time(NULL));
	//every smart gun device starts with "SGD:"
	sgdId[0] = 'S'; sgdId[1] = 'G'; sgdId[2] = 'D'; sgdId[3] = ':';
	for(int i = 4; i < 15; ++i) {
		int randNum = rand() % 26;
		sgdId[i] = 'A' + randNum; //incriment ascii by "randNum" to get random capital letter
	}

	sgdId[15] = '\0';

}

SGD::~SGD() {
	delete sgdId;
}

uint8_t SGD::getFlags() {
	return statusFlags;
}

void SGD::setFlags(SGD_Status status) {
	statusFlags = statusFlags | status;
	return;
}

void SGD::resetFlags(SGD_Status status) {
	statusFlags = statusFlags & (0xFF ^ status); //removes inidcated flag while leaving other flags untouched (flips bits to 1 instead of flag, which is flipped to 0)
	return;
}

char* SGD::getSgdId() {
	return sgdId;
}

