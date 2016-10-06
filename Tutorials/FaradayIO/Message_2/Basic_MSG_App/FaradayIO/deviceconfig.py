######################################################
## Device Configuration Commands
######################################################
class Device_Config_Class:
    """
    This class object provides a single object to load, create, and modify an entire Flash D device systems settings packet in one location. Default values are provided along side broken out common update functions that avoid the need to update all fields in one giant function call.
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
        """
        A sub routine that allows modification of only the basic unit parameters (see the arguments). This function updates the class object variables.

        :param config_bitmask: A bootmask for the boot configuration. Currently if BIT = 0 then the unit will perform factory reset
        :param callsign: Callsign of the device (Watch for the maximum length of 9 bytes!)
        :param id: The ID number of the local device (0-255)
        :param p3_bitmask: Boot bitmask of the Port 3 GPIO default states
        :param p4_bitmask: Boot bitmask of the Port 4 GPIO default states

        :return: Nothing

        .. todo:: Add in Port 5 default GPIO states on boot!

        """
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
        """
        A sub routine that allows modification of only the device programmed bit in the Configuration Boot bitmask. If this bit is LOW then the unit will perform factory reset on boot. This function updates the class object variables.

        :param device_programmed_bit: A value of True will perform no action on boot, A value of False will cause device factory reset on boot and set this bit HIGH when completed.

        :return: Nothing
        """

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
        """
        A sub routine that allows modification of default Port 3 GPIO boot states. This function updates the class object variables.

        :param gpio_7: Boolean value indicating Port 3 BIT 7 GPIO boot state
        :param gpio_6: Boolean value indicating Port 3 BIT 6 GPIO boot state
        :param gpio_5: Boolean value indicating Port 3 BIT 5 GPIO boot state
        :param gpio_4: Boolean value indicating Port 3 BIT 4 GPIO boot state
        :param gpio_3: Boolean value indicating Port 3 BIT 3 GPIO boot state
        :param gpio_2: Boolean value indicating Port 3 BIT 2 GPIO boot state
        :param gpio_1: Boolean value indicating Port 3 BIT 1 GPIO boot state
        :param gpio_0: Boolean value indicating Port 3 BIT 0 GPIO boot state

        :return: Nothing
        """
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
        """
        A sub routine that allows modification of default Port 4 GPIO boot states. This function updates the class object variables.

        :param gpio_7: Boolean value indicating Port 4 BIT 7 GPIO boot state
        :param gpio_6: Boolean value indicating Port 4 BIT 6 GPIO boot state
        :param gpio_5: Boolean value indicating Port 4 BIT 5 GPIO boot state
        :param gpio_4: Boolean value indicating Port 4 BIT 4 GPIO boot state
        :param gpio_3: Boolean value indicating Port 4 BIT 3 GPIO boot state
        :param gpio_2: Boolean value indicating Port 4 BIT 2 GPIO boot state
        :param gpio_1: Boolean value indicating Port 4 BIT 1 GPIO boot state
        :param gpio_0: Boolean value indicating Port 4 BIT 0 GPIO boot state

        :return: Nothing
        """
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
        """
        A sub routine that allows modification of default CC430 radio frequency and RF power settings. This function updates the class object variables.

        :param boot_frequency_mhz: Default boot frequency in MHz (Integer or float)
        :param PATable_Byte: Default boot RF Power setting (0-152) for the CC430 PA Table register

        :return: Nothing
        """
        freq_list = create_freq_list(float(boot_frequency_mhz))
        self.rf_default_boot_freq = [freq_list[2], freq_list[1], freq_list[0]]
        self.rf_PATable = PATable_Byte

    def update_gps(self, gps_boot_bitmask, latitude_str, latitude_dir_str, longitude_str, longitude_dir_str, altitude_str, altitude_units_str):
        """
        A sub routine that allows modification of default GPS location. This is used when there is no GPS lock (if desired) or no GPS available.

        This function updates the class object variables.

        :param gps_boot_bitmask: A bitmask for boot states of the GPIO (i.e Enabled/disabled).
        :param latitude_str: Default lattitude as a string (length = 9 bytes)
        :param latitude_dir_str: Default lattitude bearing direction (N/S) as a string (length = 1 byte)
        :param longitude_str: Default longitude as a string (length = 10 bytes)
        :param longitude_dir_str: Default longitude bearing direction (E/W) as a string (length = 1 byte)
        :param altitude_str: Default altitude as a string (length = 8 bytes)
        :param latitude_str: Default altitude unit (i.e. M for meters) as a string (length = 1 byte)

        :return: Nothing
        """
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
        """
        A simple function that updates only the GPS boot bitmask.

        :param gps_enable_boot: HIGH = GPS enabled on boot | LOW = GPS disabled on boot

        :return: Nothing
        """
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
        """
        A predefined routine to update the telemetry intervals and bitmasks.

        :param boot_bitmask: A bitmask controlling the enabling/disabling of telemtry transmissions on boot. See documentation for bit definitions
        :param uart_interval_seconds: Interval between UART telemetry transmissions in seconds (size = 2 bytes)
        :param rf_interval_seconds: Interval between RF telemetry transmissions in seconds (size = 2 bytes)

        :return: Nothing
        """
        self.telemetry_boot_bitmask = boot_bitmask
        self.telemtry_uart_beacon_interval= uart_interval_seconds
        self.telemetry_rf_beacon_interval = rf_interval_seconds

    def update_bitmask_telemetry_boot(self, rf_beacon_boot, uart_beacon_boot):
        """
        A function to update only the telemetry booth bitmask bits.

        :param rf_beacon_boot: HIGH = RF telemetry transmissions enabled on boot | LOW = RF telemetry transmissions disabled on boot
        :param uart_beacon_boot: HIGH = UART telemetry transmissions enabled on boot | LOW = RF telemetry transmissions disabled on boot

        :return: Nothing
        """
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
        """
        This function creates an entire Flash Info Segment D device configuration payload from the current values in the class object.

        :return: A complete Flash Info Segment D configuration payload as a string of bytes
        """
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