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
    print datetime.datetime.now()
    print "From %s RSSI:%s" % (test.SENDERID, test.RSSI)
    print "Printing bytes: "
    print test.DATA

    if test.ACKRequested():
	print "sending ACK"
        test.sendACK()
    
    try:
        # consume remainder of the data (drop to queue?)
        if test.DATA[0] == 3:
            print "DHT 22 temperature info from node 3"
            ba = bytearray(test.DATA[1:])
            (temperature, humidity) = struct.unpack("hh", buffer(ba))
            temp = temperature / 10.0
            humi = humidity / 10.0
            
            payload = { 'room_number': '3', 'temperature': temp }
            r = requests.post("https://usa.sepio.pl/~piotr/homeautomation/log.php", data=payload)
            payload = { 'room_number': '4', 'temperature': humi }
            r = requests.post("https://usa.sepio.pl/~piotr/homeautomation/log.php", data=payload)
    	    print "Reported temp and humidity from node 3."
    except:
        pass
    
print "shutting down"
test.shutdown()
