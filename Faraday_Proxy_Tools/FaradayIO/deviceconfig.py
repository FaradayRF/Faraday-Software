######################################################
## Device Configuration Commands
######################################################
class Device_Config_Class:
    """
    This class object provides a single object to load, creat, and modify an entire Flash D device systems settings packet in one location. Default values are provided along side broken out common update functions that avoid the need to update all fields in one giant function call.
    """
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

        pkt_struct_rf = struct.Struct('<3B1B21s')
        rf = pkt_struct_rf.pack(self.rf_default_boot_freq[0], self.rf_default_boot_freq[1], self.rf_default_boot_freq[2], self.rf_PATable, chr(0)*21)

        pkt_struct_gps = struct.Struct('<9s1s10s1s8s1sB21s')
        gps = pkt_struct_gps.pack(self.gps_latitude, self.gps_latitude_dir, self.gps_longitude, self.gps_longitude_dir, self.gps_altitude, self.gps_altitude_units, self.gps_boot_bitmask, chr(0)*21)

        pkt_struct_telemetry = struct.Struct('<BHH10s')
        telem = pkt_struct_telemetry.pack(self.telemetry_boot_bitmask, self.telemtry_uart_beacon_interval, self.telemetry_rf_beacon_interval, chr(0)*10)

        #Return full configuration update packet payload (packet payload for configuration update is just the memory allocation packet to be saved)
        return config + rf + gps + telem