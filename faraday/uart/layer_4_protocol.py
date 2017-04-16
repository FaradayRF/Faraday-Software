#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Brent
#
# Created:     27/09/2015
# Copyright:   (c) Brent 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#import Layer_2_Service
import struct
import os
import logging.config

# Start logging after importing modules
filename = os.path.abspath("loggingConfig.ini")
logging.config.fileConfig(filename)
logger = logging.getLogger('UARTStack')


def create_packet(service_number, payload_length, payload):
    #Get datagram information
    #Append service number
    #[payload, service_number]

    #Serialize packet data
    service_number_hex_byte_char = chr(service_number)
    payload_length_hex = chr(payload_length)
    datagram_ready = service_number_hex_byte_char + payload_length_hex + str(payload)

    #Return packet
    return datagram_ready


def parse_packet(datagram):
    #Parse Layer 4 datagram
    parsedpacket = struct.unpack('BB123s', datagram)

    #Return parsed datagram
    return parsedpacket
