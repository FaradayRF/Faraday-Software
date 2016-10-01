#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Brent
#
# Created:     24/05/2016
# Copyright:   (c) Brent 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import struct

##########
## This script module provides functionality to decode basic Faraday packets.
##########

def parse_transport_datagram(datagram):
    """
    This function parses the RAW Faraday Transport Layer (Layer 4) datagram and returns a list containing the parsed results.
    """
    return struct.unpack('3B120s',datagram)

def parse_telemetry_packet_3(packet):
    """
    This function parses the Faraday Telemetry Packet #3 and returns a list containing the parsed results.
    """
    return struct.unpack('>9s2B9s8B1H9s1c10s1c8s1c5s1c4s3B9H2c27s', packet)

def parse_telemetry_packet_3_checksum(packet):
    """
    This function parses the Faraday Transport datagram packet specifically regarding the checksum fields and returns a list containing the parsed results.
    This function exists so that it is easy to parse the checksum ONLY from the entire packet for extractions and validation.
    """
    return struct.unpack('>91x1H27x', packet)


def compute_checksum_16(packet, length):
    """
    This function implements the Faraday checksum calculation for checksum 16 on a packet.
    """
    parsed_data = struct.unpack(str(length) + 'B', packet)
    checksum = 0

    #Add up all packet bytes (besides checksum bytes) to calculate the packets error detection 16 bit checksum value for cross reference.
    for i in range(0,len(parsed_data)):
        checksum += parsed_data[i]

    #Since python doesn't limit to 16 bit Int's like CC430 in Faraday check for overflow of 16 bits and reduce until valid 16bit value.
    while(checksum > 2**16):
        print "REDUCING", checksum
        checksum -= 2**16

    #Return checksum result
    return checksum