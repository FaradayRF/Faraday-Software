"""
This module contains GPIO bitmask allocation definitions for use with the GPIO update commands.
"""
#Port 3


LED_2 = 0b10000000 # Bit 7
LED_1 = 0b01000000 # Bit 6
GPS_STANDBY = 0b00010000 # Bit 4
GPS_RESET = 0b00001000 # Bit 3
DIGITAL_IO_0 = 0b00000001 # Bit 0
DIGITAL_IO_1 = 0b00000010 # Bit 1
DIGITAL_IO_2 = 0b00000100 # Bit 2

#Port 4

DIGITAL_IO_3 = 0b00010000 # Bit 4
DIGITAL_IO_4 = 0b00001000 # Bit 3
DIGITAL_IO_5 = 0b00000100 # Bit 2
DIGITAL_IO_6 = 0b00000010 # Bit 1
DIGITAL_IO_7 = 0b00000001 # Bit 0

#Port 5
DIGITAL_IO_8 = 0b00000100 # Bit 2
MOSFET_CNTL = 0b00010000 # Bit 4
