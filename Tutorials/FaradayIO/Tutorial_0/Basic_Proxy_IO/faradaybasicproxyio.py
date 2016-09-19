#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Brent
#
# Created:     23/08/2016
# Copyright:   (c) Brent 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import json
import requests
import base64
import time

class proxyio(object):
    def __init__(self):
        #Definitions
        self.FLASK_PORT = 80 #TCP port
        self.TELEMETRY_PORT = 5 #Faraday Transport "Service Number"
        self.CMD_UART_PORT = 2 #Faraday COMMAND "Service Number"
        self.MAXPOSTPAYLOADLEN = 124 #123

    #Functions

    def POST(self, local_device_callsign, local_device_id, uart_port, data):
        """
        This function provides a means to POST data to the Faraday proxy RESTful API. A callsign and ID of the local unit assigment (to handle multiple local units attached without COM port specifics - See config file.)
        A faraday transport layer service "port" number is also accepted so that the intented port on the faraday applications can be targeted.

        NOTE: Only a single data item is currently accepted.

        Returns:
        FLASK POST status result
        """
        #Check if payload too large
        if(len(data)>self.MAXPOSTPAYLOADLEN):
            return False #Too large!
        else:
            #Convert supplied data into BASE64 encoding for safe network transmission
            b64_data = base64.b64encode(data) #Converts to Base64
            payload = {'data' : [b64_data]}


            #POST data to UART service port
            status = requests.post("http://127.0.0.1:" + str(self.FLASK_PORT) + "/post?" + "callsign=" + str(local_device_callsign).upper() + '&port=' + str(uart_port) + '&' + 'nodeid=' + str(local_device_id), json = payload) #Sends Base64 config flash update packet to Faraday

            #Return
            return status

    def GET(self, local_device_callsign, local_device_id, uart_service_number):
        """
        This function returns a dictionary of all data packets waiting a Flask API interface queue as specified by the supplied
        UART Port (Service Number).
        """
        try:
            flask_obj = requests.get('http://127.0.0.1:' + str(self.FLASK_PORT) + '/faraday/' + str(uart_service_number)) #calling IP address directly is much faster than localhost lookup
            return json.loads(flask_obj.text)
        except:
            return False

    def GETWait(self, local_device_callsign, local_device_id, uart_service_number, sec_timeout, debug):
        """
        This is an abstraction of function "GetPortJson" that implements a timing funtionality to waiting until a packet has been received (if none in queue) and returns the first received packet(s) or timesout and returns False.
        Note that this does not gaurentee that the packet received is the one intended!
        - uart_service_number = UART Service Port that is to be recevied from (Transport layer)
        - Timeout is in seconds and is a float (can be smaller than 1 seconds)
        - debug: Default=False, True = prints rolling time to recevied data
        """
        #Start timer "Start Time" and configure function variables to initial state
        starttime = time.time()
        timedelta = 0
        rx_data = False

        while((rx_data == False) and (timedelta<sec_timeout)):
            #Update new timedelta
            timedelta = time.time()-starttime
            time.sleep(0.01) #Need to add sleep to allow threading to go and GET a new packet if it arrives. Why 10ms?

            #Attempt to get data
            rx_data = self.GET(local_device_callsign, local_device_id, uart_service_number)
        #Determine if timeout or got data
        if(rx_data != False):
            if(debug):
                print "Got Data!", "Time Inwaiting:", timedelta, "Seconds"
            else:
                pass
            return rx_data
        else:
            if(debug):
                print "Failed to get data!", "Timeout =", sec_timeout
            return False


    def FlushRxPort(self, local_device_callsign, local_device_id, uart_service_number):
        """
        This is a dummy retrieval of data from a port with NO return of the data to mimic a "flushing" of a port of old data.
        Returns True if successful and False if error.
        """
        data = True
        while(data != False):
            try:
                self.GET(local_device_callsign, local_device_id, uart_service_number)
                return True
            except:
                return False

    def DecodeJsonItemRaw(self, jsonitem):
        """
        This function returns the decode (BASE64) data from a supplied encoded data packet. This function handle 1 packet at a time and returns only the resulting decoded data
        """
        data_packet = jsonitem
        decoded_data_packet = base64.b64decode(data_packet)
        return decoded_data_packet






