#!/usr/bin/env python2

import RFM69
from RFM69registers import *
import datetime
import time
from struct import *

print "pre-initialized"
test = RFM69.RFM69(RF69_915MHZ, 1, 100, isRFM69HW = True, intPin = 12)
print "class initialized"
print "reading all registers"
results = test.readAllRegs()
for result in results:
    print result
print "Performing rcCalibration"
test.rcCalibration()
print "setting high power"
test.setHighPower(False)
print "Checking temperature"
print test.readTemperature(0)
print "setting encryption"
test.encrypt(0);
#print "entering promiscuous (bug in atmega - sends to itself)"
test.promiscuous(True)
#print "sending blah to 3"
#test.send(3, "blah")
#if test.sendWithRetry(2, "blah", 3, 20):
#    print "ack recieved"
print "reading"
while True:
    test.receiveBegin()
    print test.DATALEN
    while not test.receiveDone():
        time.sleep(.1)
    print "%s from %s RSSI:%s" % ("".join([chr(letter) for letter in test.DATA]), test.SENDERID, test.RSSI)
    print test.DATA
    
    if test.ACKRequested():
	print "sending ACK"
        test.sendACK()
print "shutting down"
test.shutdown()
