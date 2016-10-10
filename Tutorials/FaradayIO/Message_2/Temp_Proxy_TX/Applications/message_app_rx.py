#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Brent
#
# Created:     12/06/2016
# Copyright:   (c) Brent 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import json
import requests
import base64
import time
import message_application

rx_message = ''
sender_callsign = ''
sender_id = 0

def getMsg_Json(flask_port, uart_port):
    try:
        flask_obj = requests.get('http://127.0.0.1:' + str(flask_port) + '/faraday/' + str(uart_port))
        return json.loads(flask_obj.text)
    except:
        return False


def printMsgJson(msg_json):
    try:
        for keys in msg_json:
            print base64.b64decode(keys['data'])
    except:
        return False

def parseMsgJson(msg_json):
    try:
        msg_list = []
        for keys in msg_json:
            msg_list.append(base64.b64decode(keys['data']))
        return msg_list
    except:
        return False

def ParseRfPkt(packet):
    return message_application.ParseRfPkt(packet)



def ParseRfPktFunction(packet):
    global rx_message, sender_callsign, sender_id
    try:
        parsed_packet = ParseRfPkt(items)
        #print "Sequence #:", parsed_packet[0]
        #print "Payload:", parsed_packet
        sequence = parsed_packet[0]
        datagram = parsed_packet[1]
        error_detect_0 = parsed_packet[2]
        error_detect_1 = parsed_packet[3]
        #Create messege to append

        if(sequence == 0):
            #print"SOH Detected", datagram
            #print len(datagram)
            pkt_soh = message_application.ParseMsgPkt_SOH(datagram)
            #print pkt_soh, pkt_soh[0], pkt_soh[1]
            rx_message = ''
            sender_callsign = pkt_soh[0][0:int(pkt_soh[1])]
            sender_id = pkt_soh[2]
            #print "Sender:", sender_callsign, '-', str(sender_id)

        elif(sequence == 255):
            #print "EOT Detected", datagram
            print sender_callsign + '-' + str(sender_id) +':', rx_message
        else:
            #print"Message Fragement #" + str(sequence)# +':', datagram
            message = message_application.ParseMsgPkt_MSG(datagram)
            rx_message += message[0]
            #print "MSG:", rx_message
    except:
        print "Fail to parse"


while(1):
    time.sleep(0.005)
    msg_raw = getMsg_Json(80, 3)
    if(msg_raw != False):
        pack_raw = parseMsgJson(msg_raw)
        for items in pack_raw:
            #print items
            ParseRfPktFunction(items)


