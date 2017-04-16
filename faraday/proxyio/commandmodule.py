# Name:        module1
# Purpose:
#
# Author:      Brent
#
# Created:     16/05/2016
# Copyright:   (c) Brent 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import cc430radioconfig
import gpioallocations
import struct
import Checksum as checksum

COMMAND_DATAGRAM_LEN = 123
COMMAND_DATAGRAM_ERROR_DETECTION_LEN = 2
FIXED_PAYLOAD_LEN_MAX = 119
DEST_CALLSIGN_MAX_LEN = 9
FIXED_RF_PAYLOAD_LEN = 42
MAX_MEMORY_READ_LEN = 121
MAX_CALLSIGN_LEN = 9  #NOTE THAT THE DEVICE CONFIG CLASS HAS IT'S OWN DEFINITION FOR CALLSIGN LENGTH MAX!
MAX_UPDATE_PAYLOAD_LEN = 64  #121
GPIO_COMMAND_NUMBER = 5
COMMAND_UPDATE_RAM = 4
COMMAND_PARAMETER_UPDATE_RAM_PARAMETER_TELEMETRY_BITMASK = 1
COMMAND_PARAMETER_UPDATE_RAM_PARAMETER_TELEMETRY_INTERVAL = 2
TELEMETRY_BITMASK_UART_BIT = 0b00000001
TELEMETRY_BITMASK_RF_BIT = 0b00000010
UPDATE_TELEMETRY_INTERVAL_UART_COMMAND = 0
UPDATE_TELEMETRY_INTERVAL_RF_COMMAND = 1
RF_CMD_NUMBER = 9


def create_command_datagram(command, payload):
    """
    This function creates a command packet datagram that encapsulates the actual command packets to the parsed. This allows identification of packet "types" and modularity within the command system.

    :param command: The command "number" that identifies the command packet to be parsed or direct action to be taken
    :param payload: The payload for the specified command packet type. This is usually just commands full "packet" structure

    :return: A complete command datagram packet as a string of raw bytes

    .. note:: This command module has a predefined set of command number definitions for use/reference.
    """
    #Define packets
    pkt_struct1 = struct.Struct('2B')
    pkt_struct2 = struct.Struct('119s')
    pkt_struct3 = struct.Struct('>1H')

    #Determine payload length
    payload_len = len(payload)

    #Create sub packets
    pkt_a = pkt_struct1.pack(command, payload_len)
    pkt_b = pkt_struct2.pack(payload)
    checksum_computed = checksum.compute_checksum_16(pkt_a + pkt_b, len(pkt_a + pkt_b))
    pkt_c = pkt_struct3.pack(checksum_computed)

    #Concactenate sub packets into a single packet
    packet_packed = pkt_a + pkt_b + pkt_c

    #Only return packet if all variables are correctly sized
    if len(payload) <= FIXED_PAYLOAD_LEN_MAX:
        #print "Lengths", len(packet_packed)
        packet_final = packet_packed
        return packet_final
    else:
        return False
        print "ERROR - Create Command: Payload Too Long!", len(payload)


def create_rf_command_datagram(dest_callsign, dest_device_id, command, payload):
    """
    This function creates a command packet datagram for commanding REMOTE (RF) Faraday devices. This datagram encapsulates the actual command packets to the passed to the remote device as a payload.

    The important difference between the RF and non RF command packet functions are remote callsign and ID arguments that tell Faraday what devices to target for commanding.

    .. note:: Remote commanding simply calls a specific local command that transmits a "local" command packet as a payload to the target Faraday device. Also, This command module has a predefined set of command number definitions for use/reference.

    :param dest_callsign: The callsign of the target Faraday unit
    :param dest_device_id: The device ID number of the target Faraday unit
    :param command: The command "number" that identifies the command packet to be parsed or direct action to be taken
    :param payload: The payload for the specified command packet type. This is usually just commands full "packet" structure

    :return: A complete command datagram packet as a string of raw bytes

    """
    #Cheack if callsign is too long
    if len(dest_callsign) < DEST_CALLSIGN_MAX_LEN:
        #Define packet structures
        pkt_cmd_datagram_struct = struct.Struct('2B25s')  #Command packect to be run on remote unit as local command
        pkt_cmd_datagram_error_detection_struct = struct.Struct('>1H')  #Command packect to be run on remote unit as local command Error Detection
        pkt_rf_cmd_struct = struct.Struct('9s2B29s')  #RF Command packet that encapsulates local command to be run on remote unit
        pkt_rf_error_detection_struct = struct.Struct('>1H')  #16bit Error Detection (Checksum)

        #Create local command for remote unit
        pkt_cmd_datagram = pkt_cmd_datagram_struct.pack(command, len(payload), payload)
        pkt_cmd_datagram_error_detection = pkt_cmd_datagram_error_detection_struct.pack(checksum.compute_checksum_16(pkt_cmd_datagram, len(pkt_cmd_datagram)))
        pkt_cmd_datagram_final = pkt_cmd_datagram + pkt_cmd_datagram_error_detection
        print repr(pkt_cmd_datagram_final)

        #Create RF Command for local device without Error Detection appended. NOTE Callsign must be in uppercase!
        pkt_rf_cmd = pkt_rf_cmd_struct.pack(str(dest_callsign).upper(), len(dest_callsign), dest_device_id, pkt_cmd_datagram_final)

        #Create final local command packet with Error Detection appeneded
        pkt_rf_error_detection = pkt_rf_error_detection_struct.pack(checksum.compute_checksum_16(pkt_rf_cmd, len(pkt_rf_cmd)))
        packet = pkt_rf_cmd + pkt_rf_error_detection
        return packet
    else:
        print "Error: Callsign too long!"


def create_fixed_length_packet(data, fixed_legth):
        """
        A simple function that accepts a string of databytes and appends padding bytes up to a fixed length.

        :param data: The string of bytes that will be appdended padding bytes to create the fixed length packet
        :param fixed_length: The length of the fixed length packet in bytes

        :return: Returns the "data" padded with additional bytes in the fixed sized specified.

        :Example:

            >>> testdata = create_fixed_length_packet("Test data message", 20)
            >>> print repr(testdata)
            'Test data message\x00\x00\x00'

        .. note:: This should be updated so that the padding byte can be specified as well.
        """
        pad_len = fixed_legth - len(data)
        pad = chr(0x00) * pad_len
        padded_data = data + pad
        return padded_data


def create_fixed_length_packet_padding(data, fixed_legth, padding_byte):
    """
    A simple function that accepts a string of databytes and appends padding bytes up to a fixed length. This version
    of the packing routine allows for the selection of a specific padding byte.

    :param data: The string of bytes that will be appdended padding bytes to create the fixed length packet
    :param fixed_length: The length of the fixed length packet in bytes
    :param padding_byte: The byte to use as padding

    :return: Returns the "data" padded with additional bytes in the fixed sized specified.

    :Example:

        >>> testdata = create_fixed_length_packet_padding("Test data message", 20, 0x7E)
        >>> print testdata
        'Test data message~~~'

    .. note:: This should be updated so that the padding byte can be specified as well.
    """
    pad_len = fixed_legth - len(data)
    pad = chr(padding_byte) * pad_len
    padded_data = data + pad
    return padded_data


def create_fixed_length_packet_leading_padding(data, fixed_legth, padding_byte):
    """
    A simple function that accepts a string of databytes and prepends padding bytes up to a fixed length. This version
    of the packing routine allows for the selection of a specific padding byte.

    :param data: The string of bytes that will be prepended padding bytes to create the fixed length packet
    :param fixed_length: The length of the fixed length packet in bytes
    :param padding_byte: The byte to use as padding

    :return: Returns the "data" padded with additional bytes in the fixed sized specified.

    :Example:

        >>> testdata = create_fixed_length_packet_leading_padding("Test data message", 20, 0x7E)
        >>> print testdata
        '~~~Test data message'

    .. note:: This should be updated so that the padding byte can be specified as well.
    """
    pad_len = fixed_legth - len(data)
    pad = chr(padding_byte) * pad_len
    padded_data = pad + data
    return padded_data


######################################################
## Misc. Faraday Functions
######################################################
def create_freq_list(freq):
    """
    This function creates the CC430 list of 3 bytes from a given input frequency.

    :param freq: Frequency in MHz as an Integer or Float

    :Return: A list of 3 bytes coresponding to the expected CC430 register settings for the given frequency. The fourth index item is the actual frequency set due to the PLL increment size.

    :Example:

        >>> create_freq_list(915.350)
        [35, 52, 173, 915.349884]


    """
    frequency_list = cc430radioconfig.freq0_carrier_calculation(26, freq, 0)
    return frequency_list


def calc_radio_freq(freq0, freq1, freq2):
    """
    This function is a reverse frequency calcuation routine that accepts the CC430 RF frequency register bytes and computes the effective frequency.

    :param freq0: Frequency byte index 0
    :param freq1: Frequency byte index 1
    :param freq2: Frequency byte index 2

    :Return: Returns the frequency in MHz as a Float.

    :Example:
        >>> calc_radio_freq(35, 52, 173)
        915.3498840332031
    """
    frequency = cc430radioconfig.freq0_reverse_carrier_calculation(26, freq0, freq1, freq2, False)
    return frequency


######################################################
## GPIO Command
######################################################
def create_gpio_cmd_bitmask(bit_number):
    """
    A simple function that creates a bitmask given the single bit location passed as an argument. This is useful for creating larger bitmasks specifically when creating bitmasks that control the GPIO functionality.

    :param bit_number: The bit location in the bitmask (MSB)

    :Return: Returns a bitmask with the signle supplied bit location HIGH.

    :Example:

        >>> create_gpio_cmd_bitmask(0)
        1
        >>> create_gpio_cmd_bitmask(4)
        16
        >>> create_gpio_cmd_bitmask(0) | create_gpio_cmd_bitmask(4)
        17

    """
    #This function is a sub-routine to simply create a single byte and bit bitmask.
    #A full bitmask can be made by OR'ing multiple bits to a single byte
    return 1 << bit_number


def create_gpio_command_packet(port3_on_bitmask, port4_on_bitmask, port5_on_bitmask, port3_off_bitmask, port4_off_bitmask, port5_off_bitmask):
    """
    A packet generation function to create the command applications "GPIO" command packet. This command packet toggles all GPIO's (that are allowed) on GPIO ports 3, 4, and 5. Note that a "0" within a bitmask will have *no affect* whereas a "1" in a bitmask will perform the HIGH or LOW toggling respectively.

    :param p3_bitmask_on: A 1 byte bitmask for PORT 3 GPIO that if bit HIGH it will toggle the corresponding GPIO HIGH. If bit is LOW it will have no affect on the corresponding GPIO.
    :param p4_bitmask_on: A 1 byte bitmask for PORT 4 GPIO that if bit HIGH it will toggle the corresponding GPIO HIGH. If bit is LOW it will have no affect on the corresponding GPIO.
    :param p5_bitmask_on: A 1 byte bitmask for PORT 5 GPIO that if bit HIGH it will toggle the corresponding GPIO HIGH. If bit is LOW it will have no affect on the corresponding GPIO.
    :param p3_bitmask_off: A 1 byte bitmask for PORT 3 GPIO that if bit HIGH it will toggle the corresponding GPIO LOW. If bit is LOW it will have no affect on the corresponding GPIO.
    :param p4_bitmask_off: A 1 byte bitmask for PORT 4 GPIO that if bit HIGH it will toggle the corresponding GPIO LOW. If bit is LOW it will have no affect on the corresponding GPIO.
    :param p5_bitmask_off: A 1 byte bitmask for PORT 5 GPIO that if bit HIGH it will toggle the corresponding GPIO LOW. If bit is LOW it will have no affect on the corresponding GPIO.

    :Return: Returns the complete GPIO command application packet with the supplied bitmasks

    :Example: Example using both the GPIO command bitmask function and an integer input bitmask

        >>> create_gpio_command_packet(create_gpio_cmd_bitmask(6), 0, 0, 1, 0, 0)

    """
    #This function is the create a single ON/OFF for all GPIO ports
    #Define Packets Structures
    gpio_cmd_pkt_struct = struct.Struct('6B')

    #Create ON/OFF integers to bitwise & to check for duplicate bits for bot ON and OFF
    check_on_int = port3_on_bitmask << 16
    check_on_int |= port4_on_bitmask << 8
    check_on_int |= port5_on_bitmask
    check_off_int = port3_off_bitmask << 16
    check_off_int |= port4_off_bitmask << 8
    check_off_int |= port5_off_bitmask
    if (check_on_int & check_off_int) != 0:
        print "GPIO ON/OFF Bitmask check FAIL"
        return False
    else:
        gpio_cmd_pkt = gpio_cmd_pkt_struct.pack(port3_on_bitmask, port4_on_bitmask, port5_on_bitmask, port3_off_bitmask, port4_off_bitmask, port5_off_bitmask)
        return gpio_cmd_pkt  #create_command_packet(GPIO_COMMAND_NUMBER, gpio_command_packet)


def packet_gpio_gps_standby_enable():
    """
    A predefined funtion that returns the GPIO bitmask to ENABLE the GPS standby GPIO pin.

    :Return: A GPIO Bitmask

    .. todo:: This function needs updating to the new create_gpio_command_packet()
    """
    return create_gpio_command_packet(3, gpioallocations.GPS_STANDBY, 0)


def packet_gpio_gps_standby_disable():
    """
    A predefined funtion that returns the GPIO bitmask to DISABLE the GPS standby GPIO pin.

    :Return: A GPIO Bitmask

    .. todo:: This function needs updating to the new create_gpio_command_packet()
    """
    return create_gpio_command_packet(3, gpioallocations.GPS_STANDBY, 1)


def packet_gpio_gps_reset_enable():
    """
    A predefined funtion that returns the GPIO bitmask to ENABLE the GPS RESET GPIO pin.

    :Return: A GPIO Bitmask

    .. todo:: This function needs updating to the new create_gpio_command_packet()
    """
    return create_gpio_command_packet(3, gpioallocations.GPS_RESET, 0)


def packet_gpio_gps_reset_disable():
    """
    A predefined funtion that returns the GPIO bitmask to DISABLE the GPS RESET GPIO pin.

    :Return: A GPIO Bitmask

    .. todo:: This function needs updating to the new create_gpio_command_packet()
    """
    return create_gpio_command_packet(3, gpioallocations.GPS_RESET, 1)


def packet_gpio_mosfet_enable():
    """
    A predefined funtion that returns the GPIO bitmask to ENABLE the MOSFET GPIO pin.

    :Return: A GPIO Bitmask

    .. todo:: This function needs updating to the new create_gpio_command_packet()
    """
    return create_gpio_command_packet(5, gpioallocations.MOSFET_CNTL, 1)


def packet_gpio_mosfet_disable():
    """
    A predefined funtion that returns the GPIO bitmask to DISABLE the MOSFET GPIO pin.

    :Return: A GPIO Bitmask

    .. todo:: This function needs updating to the new create_gpio_command_packet()
    """
    return create_gpio_command_packet(5, gpioallocations.MOSFET_CNTL, 0)


def packet_gpio_led_1_enable():
    """
    A predefined funtion that returns the GPIO bitmask to ENABLE the LED #1 GPIO pin.

    :Return: A GPIO Bitmask

    .. todo:: This function needs updating to the new create_gpio_command_packet()
    """
    return create_gpio_command_packet(3, gpioallocations.LED_1, 1)


def packet_gpio_led_1_disable():
    """
    A predefined funtion that returns the GPIO bitmask to DISABLE the LED #1 GPIO pin.

    :Return: A GPIO Bitmask

    .. todo:: This function needs updating to the new create_gpio_command_packet()
    """
    return create_gpio_command_packet(3, gpioallocations.LED_1, 0)


def packet_gpio_led_2_enable():
    """
    A predefined funtion that returns the GPIO bitmask to ENABLE the LED #2 GPIO pin.

    :Return: A GPIO Bitmask

    .. todo:: This function needs updating to the new create_gpio_command_packet()
    """
    return create_gpio_command_packet(3, gpioallocations.LED_2, 1)


def packet_gpio_led_2_disable():
    """
    A predefined funtion that returns the GPIO bitmask to DISABLE the LED #2 GPIO pin.

    :Return: A GPIO Bitmask

    .. todo:: This function needs updating to the new create_gpio_command_packet()
    """
    return create_gpio_command_packet(3, gpioallocations.LED_2, 0)


##############
## Command = READ MEMORY
##############
def create_read_memory_packet(dec_address, length):
    """
    This function returns the command packet that commands the Faraday device to return the memory contents of the specified memory location (CC430) and of specific length

    .. note:: The length cannout be larger than the maximum transmisible unit.

    :param dec_address: the starting locaton memory address (integer) to be returned
    :param length: The length in bytes that are to be read and returned

    :Return: A string of bytes that are the values in memory of the specified memory location

    :Example:

        >>> create_read_memory_packet(0x1800, 10)
        '\x18\x00\n'

    """
    if length <= MAX_MEMORY_READ_LEN:
        packet_struct = struct.Struct('>HB')
        packet = packet_struct.pack(dec_address, length)
        return packet
    else:
        return False


##############
## Command = UPDATE DEVICE RAM PARAMETERS
##############

##def create_ram_update_packet(parameter, data):
##    if(len(data)<MAX_UPDATE_PAYLOAD_LEN):
##            packet_struct = struct.Struct('>B'+ str(MAX_UPDATE_PAYLOAD_LEN) + 's')
##            packet = packet_struct.pack(parameter, data)
##            return packet
##    else:
##        return False

##def create_update_callsign_packet(callsign, device_id):
##    callsign_length = len(callsign)
##    if(callsign_length<MAX_CALLSIGN_LEN):
##        packet_struct = struct.Struct('>B9sB')
##        packet = packet_struct.pack(callsign_length, str(callsign).upper(), int(device_id))
##        packet = create_command_packet(0, packet) # 0 - Is callsign update RAM command.
##        return packet
##    else:
##        return False


##def create_update_telemetry_bitmask(bitmask, command):
##    packet_struct = struct.Struct('>2B')
##    return packet_struct.pack(bitmask, command)
##
##def create_update_telemetry_uart_bitmask_enable():
##    return create_ram_update_packet(COMMAND_PARAMETER_UPDATE_RAM_PARAMETER_TELEMETRY_BITMASK,create_update_telemetry_bitmask(TELEMETRY_BITMASK_UART_BIT,1))
##
##def create_update_telemetry_uart_bitmask_disable():
##    return create_ram_update_packet(COMMAND_PARAMETER_UPDATE_RAM_PARAMETER_TELEMETRY_BITMASK,create_update_telemetry_bitmask(TELEMETRY_BITMASK_UART_BIT,0))
##
##def create_update_telemetry_rf_bitmask_enable():
##    return create_ram_update_packet(COMMAND_PARAMETER_UPDATE_RAM_PARAMETER_TELEMETRY_BITMASK,create_update_telemetry_bitmask(TELEMETRY_BITMASK_RF_BIT,1))
##
##def create_update_telemetry_rf_bitmask_disable():
##    return create_ram_update_packet(COMMAND_PARAMETER_UPDATE_RAM_PARAMETER_TELEMETRY_BITMASK,create_update_telemetry_bitmask(TELEMETRY_BITMASK_RF_BIT,0))
##
##def create_update_telemetry_interval(command, interval):
##    packet_struct = struct.Struct('<BH')
##    return packet_struct.pack(command, int(interval))
##
##def create_update_telemetry_interval_uart_packet(interval):
##    return create_ram_update_packet(COMMAND_PARAMETER_UPDATE_RAM_PARAMETER_TELEMETRY_INTERVAL,create_update_telemetry_interval(UPDATE_TELEMETRY_INTERVAL_UART_COMMAND, interval))
##
##def create_update_telemetry_interval_rf_packet(interval):
##    return create_ram_update_packet(COMMAND_PARAMETER_UPDATE_RAM_PARAMETER_TELEMETRY_INTERVAL,create_update_telemetry_interval(UPDATE_TELEMETRY_INTERVAL_RF_COMMAND, interval))

##############
## Command = Send Local telemetry UART Data Now
##############

def create_local_telem_update_packet():
    """
    A predefined command packet generator that provides a payload for the local telemetry update command.

    :Return: A completed packet

    .. todo:: This should be deprecated into a single "dummy" payload function
    """
    packet_struct = struct.Struct('>B')
    packet = packet_struct.pack(255)
    return packet


##############
## Command = Send RF Data Now
##############
def create_rf_telem_update_packet():
    """
    A predefined command packet generator that provides a payload for the RF telemetry update command.

    :Return: A completed packet

    .. todo:: This should be deprecated into a single "dummy" payload function
    """
    packet_struct = struct.Struct('>B')
    packet = packet_struct.pack(255)
    return packet


##############
## Command = Update RF frequency
##############
def create_update_rf_frequency_packet(frequency_mhz):
    """
    This function generates the command packet that updates the Faraday CC430 radio frequency.

    :param frequency_mhz: The frequency in MHz as an Integer or Float.

    :Return: A completed packet (string of bytes)

    """
    freq_list = create_freq_list(float(frequency_mhz))
    packet_struct = struct.Struct('3B')
    packet = packet_struct.pack(freq_list[0], freq_list[1], freq_list[2])
    return packet


##############
## Command = Change CC430 PATable Settings
## ucharPATable_Setting = Byte that is places into the PA Table
##############
def create_update_rf_patable_packet(ucharPATable_Setting):
    """
    This function generates the command packet that updates the Faraday CC430 RF power setting.

    .. note:: A setting of 152 is the maximum output power, any number higher than 152 will be sent as a value of 152.

    :param ucharPATable_Setting: The RF power table register setting byte for the CC430.

    :Return: A completed packet (string of bytes)

    """
    packet_struct = struct.Struct('1B')
    packet = packet_struct.pack(ucharPATable_Setting)
    return packet


##############
## Command = RESET device debug Flash
## Note: Not payload packet needed, returing 1 byte of 0 just for placeholder
##############
def create_reset_device_debug_flash_packet():
    """
    A predefined command that causes the flash debug memory values to RESET.

    :Return: A completed packet (string of bytes)
    """
    packet_struct = struct.Struct('1B')
    packet = packet_struct.pack(0)
    return packet


##############
## Command = Send telemetry UART device debug
## Note: Not payload packet needed, returing 1 byte of 0 just for placeholder
##############
def create_send_telemetry_device_debug_flash():
    """
    A predefined command that causes the telemetry application to send its flash debug memory values.

    :Return: A completed packet (string of bytes)
    """
    packet_struct = struct.Struct('1B')
    packet = packet_struct.pack(0)
    return packet


def create_empty_command_packet():
    """
    A predefined command that returns a simple empty command packet used as payload for commands simply needed the
    command "number" and no other payload data to accompany.

    :Return: A completed packet (string of bytes)
    """
    packet_struct = struct.Struct('1B')
    packet = packet_struct.pack(0)
    return packet


##############
## EXPERIMENTAL MESSAGE APPLICATION
##############

def CreatePacketMsgExperimental(msg_cmd, dest_callsign, dest_device_id, data_len, data):
    """
    This function creates the command packet expected by the command application routine that forwards a supplied payload over RF to a remote Faraday device. This is a very useful yet simple and un-optimized method of sending abritray data from one unit to another.

    :param dest_callsign: The callsign of the target Faraday unit
    :param dest_device_id: The device ID number of the target Faraday unit
    :param data_len: The length in bytes of the data payload supplied
    :param data: The data payload to be sent to the remote Faraday device over RF

    :Return: A completed packet (string of bytes)

    .. note: The data payload length cannot be larger than the maximum transmissible unit. Also, data only needs to be a string of bytes so both strings and packed binary data are acceptable.

    :Example: Creates an experiement message packet that sends "Testing" to the remote unit.

        >>> CreatePacketMsgExperimental(0, "KB1LQD", 1, 7, "Testing")


    """
    packet_struct = struct.Struct('1B9s2B42s')
    packet = packet_struct.pack(msg_cmd, str(dest_callsign).upper(), dest_device_id, data_len, data)
    return packet
