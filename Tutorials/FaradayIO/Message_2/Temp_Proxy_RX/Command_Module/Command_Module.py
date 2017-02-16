# Name:        module1
# Purpose:
#
# Author:      Brent
#
# Created:     16/05/2016
# Copyright:   (c) Brent 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import CC430_Radio_Config
import struct
import gpio_allocation
import Checksum as checksum

COMMAND_DATAGRAM_LEN = 123
COMMAND_DATAGRAM_ERROR_DETECTION_LEN = 2
FIXED_PAYLOAD_LEN_MAX = 119
DEST_CALLSIGN_MAX_LEN = 9
FIXED_RF_PAYLOAD_LEN = 42
MAX_MEMORY_READ_LEN = 121
MAX_CALLSIGN_LEN = 9 #NOTE THAT THE DEVICE CONFIG CLASS HAS IT'S OWN DEFINITION FOR CALLSIGN LENGTH MAX!
MAX_UPDATE_PAYLOAD_LEN = 121
GPIO_COMMAND_NUMBER = 5
COMMAND_UPDATE_RAM = 4
COMMAND_PARAMETER_UPDATE_RAM_PARAMETER_TELEMETRY_BITMASK = 1
COMMAND_PARAMETER_UPDATE_RAM_PARAMETER_TELEMETRY_INTERVAL = 2
TELEMETRY_BITMASK_UART_BIT = 0b00000001
TELEMETRY_BITMASK_RF_BIT = 0b00000010
UPDATE_TELEMETRY_INTERVAL_UART_COMMAND = 0
UPDATE_TELEMETRY_INTERVAL_RF_COMMAND = 1
RF_CMD_NUMBER = 9

def create_command_packet(command, payload):
    """
    Create Command Packet is a function that is used to form a packet intended for the Faraday Command Application to send commands to the local device. Destination callsign and device ID may or may not be needed for local operation but is required for RF commands.
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
    #print "check:", checksum_computed
    pkt_c = pkt_struct3.pack(checksum_computed)

    #Concactenate sub packets into a single packet
    packet_packed = pkt_a + pkt_b + pkt_c
    #print "Pack", repr(packet_packed), len(packet_packed)

    #Only return packet if all variables are correctly sized
    if(len(payload)<=FIXED_PAYLOAD_LEN_MAX):
        print "Lengths", len(packet_packed)
        packet_final = packet_packed
        return packet_final
    else:
        print "ERROR - Create Command: Payload Too Long!", len(payload)

def create_rf_command_packet(dest_callsign, dest_device_id, command, payload):
    #Cheack if callsign is too long
    if(len(dest_callsign)<DEST_CALLSIGN_MAX_LEN):
        payload_len = len(payload)
        #Define packet structures
        pkt_cmd_datagram_struct = struct.Struct('2B25s') #Command packect to be run on remote unit as local command
        pkt_cmd_datagram_error_detection_struct = struct.Struct('>1H') #Command packect to be run on remote unit as local command Error Detection
        pkt_rf_cmd_struct = struct.Struct('9s2B29s') #RF Command packet that encapsulates local command to be run on remote unit
        pkt_rf_error_detection_struct = struct.Struct('>1H') #16bit Error Detection (Checksum)

        #Create local command for remote unit
        pkt_cmd_datagram = pkt_cmd_datagram_struct.pack(command, len(payload), payload)
        pkt_cmd_datagram_error_detection = pkt_cmd_datagram_error_detection_struct.pack(checksum.compute_checksum_16(pkt_cmd_datagram, len(pkt_cmd_datagram)))
        pkt_cmd_datagram_final  = pkt_cmd_datagram + pkt_cmd_datagram_error_detection
        print repr(pkt_cmd_datagram_final)

        #Create RF Command for local device without Error Detection appended. NOTE Callsign must be in uppercase!
        pkt_rf_cmd = pkt_rf_cmd_struct.pack(str(dest_callsign).upper(), len(dest_callsign), dest_device_id, pkt_cmd_datagram_final)

        #Create final local command packet with Error Detection appeneded
        pkt_rf_error_detection = pkt_rf_error_detection_struct.pack(checksum.compute_checksum_16(pkt_rf_cmd, len(pkt_rf_cmd)))
        packet = pkt_rf_cmd + pkt_rf_error_detection
        return packet
    else:
        print "Error: Callsign too long!"


    #

    #print repr(pkt_datagram_struct.pack(command, payload_len, payload_padded))
    #print repr(pkt_rf_struct.pack(dest_callsign, len(dest_callsign), dest_device_id, command))
    #checksum_16 = checksum.compute_checksum_16(pkt_rf_struct.pack(dest_callsign, len(dest_callsign), dest_device_id, command),pkt_rf_struct.size)
    #print pkt_rf_struct, checksum_16
    #payload_padded = pack_data(payload, FIXED_RF_PAYLOAD_LEN)
    #print "TX:", repr(payload_padded)


def pack_data(data, fixed_legth):
        pad_len = fixed_legth-len(data)
        pad = chr(0x00)*pad_len
        pad = pad#.encode('hex')
        padded_data = data + pad
        #print padded_data, padded_data.encode('hex')
        return padded_data

def create_fixed_length_packet(data, fixed_length):
    return pack_data(data, fixed_length)



######################################################
## Device Configuration Commands
######################################################
class Device_Config_Class:
    def __init__(self):
        self.basic_configuration_bitmask = 0
        self.basic_local_callsign = ''
        self.basic_local_callsign_len = 0
        self.basic_local_id = 0
        self.basic_gpio_p3_bitmask = 0
        self.basic_gpio_p4_bitmask = 0
        self.rf_default_boot_freq = {0,0,0}
        self.rf_PATable = 40 #40 Default
        self.gps_latitude =''
        self.gps_latitude_dir = ''
        self.gps_longitude = ''
        self.gps_longitude_dir = ''
        self.gps_altitude = ''
        self.gps_altitude_units = ''
        self.gps_boot_bitmask = 0
        self.telemetry_boot_bitmask = 0
        self.telemtry_uart_beacon_interval = 0
        self.telemetry_rf_beacon_interval = 0

        #Definitions
        self.MAX_CALLSIGN_LEN = 9
        self.MAX_GPS_LATITUDE_LEN = 9
        self.MAX_GPS_LATITUDE_DIR_LEN = 1
        self.MAX_GPS_LONGITUDE_LEN = 10
        self.MAX_GPS_LONGITUTDE_DIR_LEN = 1
        self.MAX_ALTITUDE_LEN = 8
        self.MAX_ALTITUDE_UNITS_LEN = 1

    def update_basic(self, config_bitmask, callsign, id, p3_bitmask, p4_bitmask):
        if(len(callsign)<=self.MAX_CALLSIGN_LEN):
            self.basic_configuration_bitmask = config_bitmask
            self.basic_local_callsign = str(callsign).upper() #Force all uppercase
            self.basic_local_callsign_len = len(callsign)
            self.basic_local_id = id
            self.basic_gpio_p3_bitmask = p3_bitmask
            self.basic_gpio_p4_bitmask = p4_bitmask
        else:
            print "ERROR: Callsign too long!"

    def update_bitmask_configuration(self, device_programmed_bit):
        bitmask = 0
        bitmask |= device_programmed_bit << 0
        #self.basic_configuration_bitmask |= bitx << 1
        #self.basic_configuration_bitmask |= bitx << 2
        #self.basic_configuration_bitmask |= bitx << 3
        #self.basic_configuration_bitmask |= bitx << 4
        #self.basic_configuration_bitmask |= bitx << 5
        #self.basic_configuration_bitmask |= bitx << 6
        #self.basic_configuration_bitmask |= bitx << 7
        return bitmask

    def update_bitmask_gpio_p3(self, gpio_7, gpio_6, gpio_5, gpio_4, gpio_3, gpio_2, gpio_1, gpio_0):
        bitmask = 0
        bitmask |= gpio_0 << 0
        bitmask |= gpio_1 << 1
        bitmask |= gpio_2 << 2
        bitmask |= gpio_3 << 3
        bitmask |= gpio_4 << 4
        bitmask |= gpio_5 << 5
        bitmask |= gpio_6 << 6
        bitmask |= gpio_7 << 7
        return bitmask

    def update_bitmask_gpio_p4(self, gpio_7, gpio_6, gpio_5, gpio_4, gpio_3, gpio_2, gpio_1, gpio_0):
        bitmask = 0
        bitmask |= gpio_0 << 0
        bitmask |= gpio_1 << 1
        bitmask |= gpio_2 << 2
        bitmask |= gpio_3 << 3
        bitmask |= gpio_4 << 4
        bitmask |= gpio_5 << 5
        bitmask |= gpio_6 << 6
        bitmask |= gpio_7 << 7
        return bitmask

    def update_rf(self, boot_frequency_mhz, PATable_Byte):
        freq_list = create_freq_list(float(boot_frequency_mhz))
        self.rf_default_boot_freq = [freq_list[2], freq_list[1], freq_list[0]]
        self.rf_PATable = PATable_Byte

    def update_gps(self, gps_boot_bitmask, latitude_str, latitude_dir_str, longitude_str, longitude_dir_str, altitude_str, altitude_units_str):
        lat_check = len(latitude_str)<=self.MAX_GPS_LATITUDE_LEN
        lat_dir_check = len(latitude_dir_str)<=self.MAX_GPS_LATITUDE_DIR_LEN
        lon_check = len(longitude_str)<=self.MAX_GPS_LONGITUDE_LEN
        lon_dir_check = len(longitude_dir_str)<=self.MAX_GPS_LONGITUTDE_DIR_LEN
        alt_check = len(altitude_str)<=self.MAX_ALTITUDE_LEN
        alt_units_check = len(altitude_units_str)<=self.MAX_ALTITUDE_UNITS_LEN

        if(lat_check and lat_dir_check and lon_check and lon_dir_check and alt_check and alt_units_check):
            self.gps_latitude = latitude_str
            self.gps_latitude_dir = latitude_dir_str
            self.gps_longitude = longitude_str
            self.gps_longitude_dir = longitude_dir_str
            self.gps_altitude = altitude_str
            self.gps_altitude_units = altitude_units_str
        else:
            print "ERROR: GPS string(s) too long"

    def update_bitmask_gps_boot(self, gps_enable_boot):
        bitmask = 0
        self.gps_boot_bitmask |= gps_enable_boot << 0
        #self.basic_configuration_bitmask |= bitx << 1
        #self.basic_configuration_bitmask |= bitx << 2
        #self.basic_configuration_bitmask |= bitx << 3
        #self.basic_configuration_bitmask |= bitx << 4
        #self.basic_configuration_bitmask |= bitx << 5
        #self.basic_configuration_bitmask |= bitx << 6
        #self.basic_configuration_bitmask |= bitx << 7
        return bitmask

    def update_telemetry(self, boot_bitmask, uart_interval_seconds, rf_interval_seconds):
        self.telemetry_boot_bitmask = boot_bitmask
        self.telemtry_uart_beacon_interval= uart_interval_seconds
        self.telemetry_rf_beacon_interval = rf_interval_seconds

    def update_bitmask_telemetry_boot(self, rf_beacon_boot, uart_beacon_boot):
        bitmask = 0
        bitmask |= uart_beacon_boot << 0
        bitmask |= rf_beacon_boot << 1
        #self.basic_configuration_bitmask |= bitx << 2
        #self.basic_configuration_bitmask |= bitx << 3
        #self.basic_configuration_bitmask |= bitx << 4
        #self.basic_configuration_bitmask |= bitx << 5
        #self.basic_configuration_bitmask |= bitx << 6
        #self.basic_configuration_bitmask |= bitx << 7
        return bitmask

    def create_config_packet(self):
        #Create
        pkt_struct_config = struct.Struct('<B9sBBBB10s')
        config = pkt_struct_config.pack(self.basic_configuration_bitmask, self.basic_local_callsign, self.basic_local_callsign_len, self.basic_local_id, self.basic_gpio_p3_bitmask, self.basic_gpio_p4_bitmask, chr(0)*10)
        #print repr(config), len(repr(config)), len(config)

        pkt_struct_rf = struct.Struct('<3B1B21s')
        rf = pkt_struct_rf.pack(self.rf_default_boot_freq[0], self.rf_default_boot_freq[1], self.rf_default_boot_freq[2], self.rf_PATable, chr(0)*21)
        #print repr(rf), len(repr(rf)), len(rf)

        pkt_struct_gps = struct.Struct('<9s1s10s1s8s1sB21s')
        gps = pkt_struct_gps.pack(self.gps_latitude, self.gps_latitude_dir, self.gps_longitude, self.gps_longitude_dir, self.gps_altitude, self.gps_altitude_units, self.gps_boot_bitmask, chr(0)*21)
        #print repr(gps), len(repr(gps)), len(gps)

        pkt_struct_telemetry = struct.Struct('<BHH10s')
        telem = pkt_struct_telemetry.pack(self.telemetry_boot_bitmask, self.telemtry_uart_beacon_interval, self.telemetry_rf_beacon_interval, chr(0)*10)

        #Return full configuration update packet payload (packet payload for configuration update is just the memory allocation packet to be saved)
        return config + rf + gps + telem

######################################################
## Misc. Faraday Functions
######################################################
def create_freq_list(freq):
    frequency_list = CC430_Radio_Config.freq0_carrier_calculation(26,freq,0)
    return frequency_list

######################################################
## GPIO Command
######################################################
def create_gpio_cmd_bitmask(bit_number):
    #This function is a sub-routine to simply create a single byte and bit bitmask.
    #A full bitmask can be made by OR'ing multiple bits to a single byte
    return (1<<bit_number)

def create_gpio_command_packet(port3_on_bitmask, port4_on_bitmask, port5_on_bitmask, port3_off_bitmask, port4_off_bitmask, port5_off_bitmask):
    #This function is the create a single ON/OFF for all GPIO ports
    #Define Packets Structures
    gpio_cmd_pkt_struct = struct.Struct('6B')

    #Create ON/OFF integers to bitwise & to check for duplicate bits for bot ON and OFF
    check_on_int = port3_on_bitmask<<16
    check_on_int |= port4_on_bitmask<<8
    check_on_int |= port5_on_bitmask
    check_off_int = port3_off_bitmask<<16
    check_off_int |= port4_off_bitmask<<8
    check_off_int |= port5_off_bitmask
    if((check_on_int&check_off_int) != 0):
        print "GPIO ON/OFF Bitmask check FAIL"
        return False
    else:
        gpio_cmd_pkt = gpio_cmd_pkt_struct.pack(port3_on_bitmask, port4_on_bitmask, port5_on_bitmask, port3_off_bitmask, port4_off_bitmask, port5_off_bitmask)
        return gpio_cmd_pkt #create_command_packet(GPIO_COMMAND_NUMBER, gpio_command_packet)

def packet_gpio_gps_standby_enable():
    return create_gpio_command_packet(3, gpio_allocation.GPS_STANDBY, 0)

def packet_gpio_gps_standby_disable():
    return create_gpio_command_packet(3, gpio_allocation.GPS_STANDBY, 1)

def packet_gpio_gps_reset_enable():
    return create_gpio_command_packet(3, gpio_allocation.GPS_RESET, 0)

def packet_gpio_gps_reset_disable():
    return create_gpio_command_packet(3, gpio_allocation.GPS_RESET, 1)

def packet_gpio_mosfet_enable():
    return create_gpio_command_packet(5, gpio_allocation.MOSFET_CNTL, 1)

def packet_gpio_mosfet_disable():
    return create_gpio_command_packet(5, gpio_allocation.MOSFET_CNTL, 0)

def packet_gpio_led_1_enable():
    return create_gpio_command_packet(3, gpio_allocation.LED_1, 1)

def packet_gpio_led_1_disable():
    return create_gpio_command_packet(3, gpio_allocation.LED_1, 0)

def packet_gpio_led_2_enable():
    return create_gpio_command_packet(3, gpio_allocation.LED_2, 1)

def packet_gpio_led_2_disable():
    return create_gpio_command_packet(3, gpio_allocation.LED_2, 0)

######################################################
## Read Memory Command
######################################################
def get_mem_addr(address, length):
    try:
        device.send_cmd_packet(2,2,device.create_memory_read_packet(address, length))
        starttime = time.time()
        time.sleep(0.5)
        data = False
        print starttime
        #while(data == False):
        #    runtime = time.time()-starttime
        #    data = device.get(2)
        #    print runtime < 3
        #print "RAW:", data
        #print "BYTES:", repr(data)
    except:
        print "Fail", data

##############
## Command = READ MEMORY
##############

def create_read_memory_packet(dec_address, length):
    if(length<=MAX_MEMORY_READ_LEN):
        packet_struct = struct.Struct('>HB')
        packet = packet_struct.pack(dec_address, length)
        return packet
    else:
        return False


##############
## Command = UPDATE DEVICE RAM PARAMETERS
##############

def create_ram_update_packet(parameter, data):
    if(len(data)<MAX_UPDATE_PAYLOAD_LEN):
            packet_struct = struct.Struct('>B'+ str(MAX_UPDATE_PAYLOAD_LEN) + 's')
            packet = packet_struct.pack(parameter, data)
            return packet
    else:
        return False

def create_update_callsign_packet(callsign, device_id):
    callsign_length = len(callsign)
    if(callsign_length<MAX_CALLSIGN_LEN):
        packet_struct = struct.Struct('>B9sB')
        packet = packet_struct.pack(callsign_length, str(callsign).upper(), int(device_id))
        packet = create_command_packet(0, packet) # 0 - Is callsign update RAM command.
        return packet
    else:
        return False


def create_update_telemetry_bitmask(bitmask, command):
    packet_struct = struct.Struct('>2B')
    return packet_struct.pack(bitmask, command)

def create_update_telemetry_uart_bitmask_enable():
    return create_ram_update_packet(COMMAND_PARAMETER_UPDATE_RAM_PARAMETER_TELEMETRY_BITMASK,create_update_telemetry_bitmask(TELEMETRY_BITMASK_UART_BIT,1))

def create_update_telemetry_uart_bitmask_disable():
    return create_ram_update_packet(COMMAND_PARAMETER_UPDATE_RAM_PARAMETER_TELEMETRY_BITMASK,create_update_telemetry_bitmask(TELEMETRY_BITMASK_UART_BIT,0))

def create_update_telemetry_rf_bitmask_enable():
    return create_ram_update_packet(COMMAND_PARAMETER_UPDATE_RAM_PARAMETER_TELEMETRY_BITMASK,create_update_telemetry_bitmask(TELEMETRY_BITMASK_RF_BIT,1))

def create_update_telemetry_rf_bitmask_disable():
    return create_ram_update_packet(COMMAND_PARAMETER_UPDATE_RAM_PARAMETER_TELEMETRY_BITMASK,create_update_telemetry_bitmask(TELEMETRY_BITMASK_RF_BIT,0))

def create_update_telemetry_interval(command, interval):
    packet_struct = struct.Struct('<BH')
    return packet_struct.pack(command, int(interval))

def create_update_telemetry_interval_uart_packet(interval):
    return create_ram_update_packet(COMMAND_PARAMETER_UPDATE_RAM_PARAMETER_TELEMETRY_INTERVAL,create_update_telemetry_interval(UPDATE_TELEMETRY_INTERVAL_UART_COMMAND, interval))

def create_update_telemetry_interval_rf_packet(interval):
    return create_ram_update_packet(COMMAND_PARAMETER_UPDATE_RAM_PARAMETER_TELEMETRY_INTERVAL,create_update_telemetry_interval(UPDATE_TELEMETRY_INTERVAL_RF_COMMAND, interval))

##############
## Command = Send Local telemetry UART Data Now
##############

def create_local_telem_update_packet():
    packet_struct = struct.Struct('>B')
    packet = packet_struct.pack(255)
    return packet

##############
## Command = Send Local telemetry RF Data Now
##############

def create_local_telem_update_packet():
    packet_struct = struct.Struct('>B')
    packet = packet_struct.pack(255)
    return packet

##############
## Command = Send RF Data Now
##############

def create_rf_telem_update_packet():
    packet_struct = struct.Struct('>B')
    packet = packet_struct.pack(255)
    return packet

##############
## Command = Update RF frequency
##############

def create_update_rf_frequency_packet(boot_frequency_mhz):
    freq_list = create_freq_list(float(boot_frequency_mhz))
    packet_struct = struct.Struct('3B')
    packet = packet_struct.pack(freq_list[0], freq_list[1], freq_list[2])
    #packet = create_command_packet(5,packet)[0:121] #BUG? This otherwise returnes 123 bytes
    return packet


##############
## Command = Change CC430 PATable Settings
## ucharPATable_Setting = Byte that is places into the PA Table
##############


def create_update_rf_patable_packet(ucharPATable_Setting):
    packet_struct = struct.Struct('1B')
    packet = packet_struct.pack(ucharPATable_Setting)
    return packet

##############
## Command = RESET device debug Flash
## Note: Not payload packet needed, returing 1 byte of 0 just for placeholder
##############
def create_reset_device_debug_flash_packet():
    packet_struct = struct.Struct('1B')
    packet = packet_struct.pack(0)
    return packet


##############
## Command = Send telemetry UART device debug
## Note: Not payload packet needed, returing 1 byte of 0 just for placeholder
##############
def create_send_telemetry_device_debug_flash():
    packet_struct = struct.Struct('1B')
    packet = packet_struct.pack(0)
    return packet

##############
## Command = Send telemetry UART device system settings
## Note: Not payload packet needed, returing 1 byte of 0 just for placeholder
##############
def create_send_telemetry_device_debug_flash():
    packet_struct = struct.Struct('1B')
    packet = packet_struct.pack(0)
    return packet
