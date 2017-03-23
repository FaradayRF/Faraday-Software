import requests
import base64
import cPickle
import time
import ConfigParser
import os

config = ConfigParser.RawConfigParser()
filename = os.path.abspath("hermes.ini")
config.read(filename)

localcallsign = config.get('UNIT0', 'CALLSIGN')
localnodeid = int(config.get('UNIT0', 'NODEID'))
destinationcallsign = config.get('UNIT1', 'CALLSIGN')
destinationnodeid = int(config.get('UNIT1', 'NODEID'))

def main():
    while 1:
        message = raw_input("Enter Message: ")
        payload = {'localcallsign': localcallsign, 'localnodeid': localnodeid, 'destinationcallsign': destinationcallsign, 'destinationnodeid': destinationnodeid, 'data': message}
        txdata = requests.post('http://127.0.0.1:8005/', params=payload)

if __name__ == '__main__':
    main()



