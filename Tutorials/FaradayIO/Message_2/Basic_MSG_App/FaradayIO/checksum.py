import struct

##########
## Checksum
##########

def compute_checksum_16(packet, length):
    """
    Computes a basic 16 bit checksum of a supplied string of bytes (packet) and length. This is used for error detection purposes.

    :param packet: The packet that the checksum will be computed as a string of bytes
    :param length: The length of the supplied packet to computer a checksum of. This allows for computing a checksome of a partial packet if needed.

    :return: Returns the 16 bit checksum as an Integer
    """
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