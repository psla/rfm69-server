#!/usr/bin/env python2

import RFM69
from RFM69registers import *
import datetime
import time
import struct
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
        time.sleep(.1)
    print "On %s from %s RSSI:%s" % (datetime.datetime.now(), test.SENDERID, test.RSSI)

    if test.ACKRequested():
	print "sending ACK"
        test.sendACK()
    
    try:
        # consume remainder of the data (drop to queue?)
        if test.DATA[0] == 3:
            # DHT 22 temperature info from node 3
            ba = bytearray(test.DATA[1:])
            # this may fail with exception if incorrect data was received -
            # add some kind of parity check unless RFM is already doing that..
            (temperature, humidity) = struct.unpack("hh", buffer(ba))
            temp = temperature / 10.0
            humi = humidity / 10.0
            
            # these can fail for various reasons (server not responding, etc.)
            # consider retry logic - keep in mind that it will block other messages from being received
            payload = { 'room_number': '3', 'temperature': temp }
            r = requests.post("https://usa.sepio.pl/~piotr/homeautomation/log.php", data=payload)
            payload = { 'room_number': '4', 'temperature': humi }
            r = requests.post("https://usa.sepio.pl/~piotr/homeautomation/log.php", data=payload)
    	    print "Reported temp and humidity from node 3."
    except Exception, err:
        print "From %s RSSI:%s" % (test.SENDERID, test.RSSI)
        print "Message that caused exception:"
        print test.DATA
        print traceback.format_exc()
    
print "shutting down"
test.shutdown()
