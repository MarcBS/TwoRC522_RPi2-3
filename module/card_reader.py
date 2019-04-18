 #!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Class in Python 2.7 that executes a Thread for reading RFID tags.

"""

import threading
import signal
import RPi.GPIO as GPIO
from gpio import PinsGPIO
from time import sleep
from MFRC522 import MFRC522
from pins import PinControl


continue_reading = True


def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    #GPIO.cleanup()

    signal.signal(signal.SIGINT, end_read)

class Nfc522(object):

    def __init__(self, spi, rst):
        self.pc = PinControl()
        self.RST = rst  # GPIO
        if spi == 0:
            self.SPI_DEV = '/dev/spidev0.0'
        elif spi == 1:
            self.SPI_DEV = '/dev/spidev0.1'
        else:
            raise Exception('Invalid spi input pin.')

        self.MIFAREReader = MFRC522(self.RST, self.SPI_DEV)


    def read_nfc_rfid(self, autenticacao=True):

        # Scan for cards
        (status,TagType) = self.MIFAREReader.MFRC522_Request(self.MIFAREReader.PICC_REQIDL)

        # If a card is found
        # if status == self.MIFAREReader.MI_OK:
            # print "Card detected"

        # Get the UID of the card
        (status,uid) = self.MIFAREReader.MFRC522_Anticoll()

        return uid

        # If we have the UID, continue
        if status == self.MIFAREReader.MI_OK:

            # Print UID
            print "Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])


            # GPIO.output(24,GPIO.HIGH)   # Code For Turn ON/OFF Buzzer
            # sleep(0.1)
            # GPIO.output(24,GPIO.LOW)

            # This is the default key for authentication
            key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]

            # Select the scanned tag
            self.MIFAREReader.MFRC522_SelectTag(uid)

            # Authenticate
            status = self.MIFAREReader.MFRC522_Auth(self.MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

            # Check if authenticated
            if status == self.MIFAREReader.MI_OK:
                self.MIFAREReader.MFRC522_Read(8)
                self.MIFAREReader.MFRC522_StopCrypto1()
            else:
                print "Authentication error"
                

class CardReader(threading.Thread):

    def __init__(self, spi, rst):
        self.nfc = Nfc522(spi, rst)
        self.card_number = None
            
    def run(self):
        print "%s. Run... " % self.name
        self.read()
        
    def get_rfid_card_number(self):
        id = None
        try:
            while True:
                id = self.nfc.read_nfc_rfid()
                if id:
                    id = str(id).zfill(10)
                    if (len(id) >= 10):
                        self.card_number = id
                        print "Read TAG Number: "+str(self.card_number)
                        return self.card_number
                    else:
                        print "Error TAG Number: " +str(self.card_number)
                        id = None
                        return None
                else:
                    return id
        except Exception as e:
            print e
            return None
            
    def read(self):
        try:
            self.get_rfid_card_number()
            return None
        except Exception as e:
            print e

