import struct

##########
## Checksum
##########

def compute_checksum_16(packet, length):
    parsed_data = struct.unpack(str(length) + 'B', packet)
    checksum = 0
    #print "TESTING ****", parsed_data
    for i in range(0,len(parsed_data)):
        checksum += parsed_data[i]
    #since python doesn't limit to 16 bit Int's like CC430 in Faraday check for overflow of 16 bits and convert
    while(checksum > 2**16):
        print "REDUCING", checksum
        checksum -= 2**16
    #Return checksum result
    return checksum