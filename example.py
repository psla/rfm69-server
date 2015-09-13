#!/usr/bin/env python2

import RFM69
from RFM69registers import *
import datetime
import time
import struct
import traceback
#from struct import *

import requests

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
test.setHighPower(True)
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
        time.sleep(.005)
    print "On %s from %s RSSI:%s" % (datetime.datetime.now(), test.SENDERID, test.RSSI)

    if test.ACKRequested():
	print "sending ACK"
        test.sendACK()
    
    try:
        # consume remainder of the data (drop to queue?)
        if test.DATA[0] == 3 or test.DATA[0] == 2:
            # DHT 22 temperature info from node 3
            ba = bytearray(test.DATA[1:5])
            # this may fail with exception if incorrect data was received -
            # add some kind of parity check unless RFM is already doing that..
            (temperature, humidity) = struct.unpack("hh", buffer(ba))
            temp = temperature / 10.0
            humi = humidity / 10.0

            checksum = sum(test.DATA[0:5]) % 256
            if checksum != test.DATA[5]:
                # TODO, in future we want to log them straight to the server, along with the request
                raise ValueError('Checksum did not match', test.DATA)
            
            # these can fail for various reasons (server not responding, etc.)
            # consider retry logic - keep in mind that it will block other messages from being received
            payload = { 'room_number': test.DATA[0], 'temperature': temp }
            r = requests.post("https://usa.sepio.pl/~piotr/homeautomation/log.php", data=payload, verify=False)
            # room_number 4 for node 3, 5 for node 2
            payload = { 'room_number': 7 - test.DATA[0], 'temperature': humi }
            r = requests.post("https://usa.sepio.pl/~piotr/homeautomation/log.php", data=payload, verify=False)
    except Exception, err:
        print "From %s RSSI:%s" % (test.SENDERID, test.RSSI)
        print "Message that caused exception:"
        print test.DATA
        traceback.print_exc()
    
print "shutting down"
test.shutdown()
