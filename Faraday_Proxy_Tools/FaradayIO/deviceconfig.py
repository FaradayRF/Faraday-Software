import struct
import cc430radioconfig
import commandmodule


class DeviceConfigClass:
    """
    This class object provides a single object to load, create, and modify an entire Flash D device systems settings
    packet in one location. Default values are provided along side broken out common update functions that avoid the
    need to update all fields in one giant function call.
    """

    def __init__(self):
        self.basic_configuration_bitmask = 0
        self.basic_local_callsign = ''
        self.basic_local_callsign_len = 0
        self.basic_local_id = 0
        self.basic_gpio_p3_bitmask = 0
        self.basic_gpio_p4_bitmask = 0
        self.basic_gpio_p5_bitmask = 0
        self.rf_default_boot_freq = {0, 0, 0}
        self.rf_PATable = 40  # 40 Default
        self.gps_latitude = ''
        self.gps_latitude_dir = ''
        self.gps_longitude = ''
        self.gps_longitude_dir = ''
        self.gps_altitude = ''
        self.gps_altitude_units = ''
        self.gps_boot_bitmask = 0
        self.telemetry_boot_bitmask = 0
        self.telemetry_uart_beacon_interval = 0
        self.telemetry_rf_beacon_interval = 0

        # Definitions
        self.MAX_CALLSIGN_LEN = 9
        self.MAX_GPS_LATITUDE_LEN = 9
        self.MAX_GPS_LATITUDE_DIR_LEN = 1
        self.MAX_GPS_LONGITUDE_LEN = 10
        self.MAX_GPS_LONGITUDE_DIR_LEN = 1
        self.MAX_ALTITUDE_LEN = 8
        self.MAX_ALTITUDE_UNITS_LEN = 1
        self.CONFIG_PACKET_LENGTH = 116

        # Packet Definitions
        self.config_pkt_struct_config = struct.Struct('<1B 9s 5B 9x 4B 21x 9s 1s 10s 1s 8s 1s 1B 21x 1B 2H 10x')

    def extract_config_packet(self, packet):
        """
            A sub routine that extracts the device configuration packet from a larger packet.

            :param packet: The supplied larger packet that encapsulates the device configuration packet to be extracted

            :return: packet[0:self.CONFIG_PACKET_LENGTH]

            """
        return packet[0:self.CONFIG_PACKET_LENGTH]

    def update_basic(self, config_bitmask, callsign, callsign_id, p3_bitmask, p4_bitmask, p5_bitmask):
        """
        A sub routine that allows modification of only the basic unit parameters (see the arguments). This function
        updates the class object variables.

        :param config_bitmask: A bootmask for the boot configuration. Currently if BIT = 0 then the unit will perform
        factory reset
        :param callsign: Callsign of the device (Watch for the maximum length of 9 bytes!)
        :param callsign_id: The ID number of the local device (0-255)
        :param p3_bitmask: Boot bitmask of the Port 3 GPIO default states
        :param p4_bitmask: Boot bitmask of the Port 4 GPIO default states
        :param p5_bitmask: Boot bitmask of the Port 5 GPIO default states

        :return: Nothing

        """
        if len(callsign) <= self.MAX_CALLSIGN_LEN:
            self.basic_configuration_bitmask = config_bitmask
            self.basic_local_callsign = str(callsign).upper()  # Force all uppercase
            self.basic_local_callsign_len = len(callsign)
            self.basic_local_id = callsign_id
            self.basic_gpio_p3_bitmask = p3_bitmask
            self.basic_gpio_p4_bitmask = p4_bitmask
            self.basic_gpio_p5_bitmask = p5_bitmask
            return True
        else:
            print "ERROR: Callsign too long!"
            return False

    def create_bitmask_configuration(self, device_programmed_bit):
        """
        A sub routine that allows modification of only the device programmed bit in the Configuration Boot bitmask. If
        this bit is LOW then the unit will perform factory reset on boot. This function updates the class object
        variables.

        :param device_programmed_bit: A value of True will perform no action on boot, A value of False will cause
        device factory reset on boot and set this bit HIGH when completed.

        :return: Nothing
        """

        bitmask = 0
        bitmask |= int(device_programmed_bit) << 0
        # self.basic_configuration_bitmask |= bitx << 1
        # self.basic_configuration_bitmask |= bitx << 2
        # self.basic_configuration_bitmask |= bitx << 3
        # self.basic_configuration_bitmask |= bitx << 4
        # self.basic_configuration_bitmask |= bitx << 5
        # self.basic_configuration_bitmask |= bitx << 6
        # self.basic_configuration_bitmask |= bitx << 7
        return bitmask

    def create_bitmask_gpio(self, gpio_7, gpio_6, gpio_5, gpio_4, gpio_3, gpio_2, gpio_1, gpio_0):
        """
        A sub routine that allows modification of default Port X GPIO boot states. This function updates the class
        object variables.

        :param gpio_7: Boolean value indicating Port X BIT 7 GPIO boot state
        :param gpio_6: Boolean value indicating Port X BIT 6 GPIO boot state
        :param gpio_5: Boolean value indicating Port X BIT 5 GPIO boot state
        :param gpio_4: Boolean value indicating Port X BIT 4 GPIO boot state
        :param gpio_3: Boolean value indicating Port X BIT 3 GPIO boot state
        :param gpio_2: Boolean value indicating Port X BIT 2 GPIO boot state
        :param gpio_1: Boolean value indicating Port X BIT 1 GPIO boot state
        :param gpio_0: Boolean value indicating Port X BIT 0 GPIO boot state

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

    def update_rf(self, boot_frequency_mhz, patable_byte):
        """
        A sub routine that allows modification of default CC430 radio frequency and RF power settings. This function
        updates the class object variables.

        :param boot_frequency_mhz: Default boot frequency in MHz (Integer or float)
        :param patable_byte: Default boot RF Power setting (0-152) for the CC430 PA Table register

        :return: Nothing
        """
        freq_list = cc430radioconfig.freq0_carrier_calculation(float(boot_frequency_mhz))  # create_freq_list(float(boot_frequency_mhz))
        self.rf_default_boot_freq = [freq_list[2], freq_list[1], freq_list[0]]
        self.rf_PATable = patable_byte
        return True



    def update_gps(self, gps_boot_bitmask, latitude_str, latitude_dir_str, longitude_str, longitude_dir_str,
                   altitude_str, altitude_units_str):
        """
        A sub routine that allows modification of default GPS location. This is used when there is no GPS lock
        (if desired) or no GPS available.

        This function updates the class object variables.

        :note This function forces "float" on: Lat, Lon, Alt.

        :param gps_boot_bitmask: A bitmask for boot states of the GPIO (i.e Enabled/disabled).
        :param latitude_str: Default latitude as a string (length = 9 bytes)
        :param latitude_dir_str: Default latitude bearing direction (N/S) as a string (length = 1 byte)
        :param longitude_str: Default longitude as a string (length = 10 bytes)
        :param longitude_dir_str: Default longitude bearing direction (E/W) as a string (length = 1 byte)
        :param altitude_str: Default altitude as a string (length = 8 bytes)
        :param altitude_units_str: Default altitude unit (i.e. M for meters) as a string (length = 1 byte)

        :return: Nothing
        """
        lat_check = len(latitude_str) <= self.MAX_GPS_LATITUDE_LEN
        lat_dir_check = len(latitude_dir_str) <= self.MAX_GPS_LATITUDE_DIR_LEN
        lon_check = len(longitude_str) <= self.MAX_GPS_LONGITUDE_LEN
        lon_dir_check = len(longitude_dir_str) <= self.MAX_GPS_LONGITUDE_DIR_LEN
        alt_check = len(altitude_str) <= self.MAX_ALTITUDE_LEN
        alt_units_check = len(altitude_units_str) <= self.MAX_ALTITUDE_UNITS_LEN

        # Prepend all Lat, Lon, Alt with (0x30) padded bytes of fixed length packet
        latitude_str = commandmodule.create_fixed_length_packet_leading_padding(str(latitude_str), self.MAX_GPS_LATITUDE_LEN, 0x30)
        longitude_str = commandmodule.create_fixed_length_packet_leading_padding(str(longitude_str), self.MAX_GPS_LONGITUDE_LEN, 0x30)
        altitude_str = commandmodule.create_fixed_length_packet_leading_padding(str(altitude_str), self.MAX_ALTITUDE_LEN, 0x30)

        if lat_check and lat_dir_check and lon_check and lon_dir_check and alt_check and alt_units_check:
            self.gps_latitude = latitude_str
            self.gps_latitude_dir = latitude_dir_str
            self.gps_longitude = longitude_str
            self.gps_longitude_dir = longitude_dir_str
            self.gps_altitude = altitude_str
            self.gps_altitude_units = altitude_units_str
            self.gps_boot_bitmask = gps_boot_bitmask

            return True

        else:
            print "ERROR: GPS string(s) too long"
            return False

    def update_bitmask_gps_boot(self, gps_present_boot, gps_enable_boot):
        """
        A simple function that updates only the GPS boot bitmask.

        HIGH = 1
        LOW = 0

        :param gps_present_boot: HIGH = GPS present (installed) by default | LOW = GPS not present (not-installed) by default
        :param gps_enable_boot: HIGH = GPS enabled on boot | LOW = GPS disabled on boot

        :return: Nothing
        """
        bitmask = 0
        bitmask |= int(gps_enable_boot) << 0
        bitmask |= int(gps_present_boot) << 1
        # self.basic_configuration_bitmask |= bitx << 2
        # self.basic_configuration_bitmask |= bitx << 3
        # self.basic_configuration_bitmask |= bitx << 4
        # self.basic_configuration_bitmask |= bitx << 5
        # self.basic_configuration_bitmask |= bitx << 6
        # self.basic_configuration_bitmask |= bitx << 7
        return bitmask

    def update_telemetry(self, boot_bitmask, uart_interval_seconds, rf_interval_seconds):
        """
        A predefined routine to update the telemetry intervals and bitmasks.

        :param boot_bitmask: A bitmask controlling the enabling/disabling of telemetry transmissions on boot. See
        documentation for bit definitions
        :param uart_interval_seconds: Interval between UART telemetry transmissions in seconds (size = 2 bytes)
        :param rf_interval_seconds: Interval between RF telemetry transmissions in seconds (size = 2 bytes)

        :return: Nothing
        """
        self.telemetry_boot_bitmask = int(boot_bitmask)
        self.telemetry_uart_beacon_interval = int(uart_interval_seconds)
        self.telemetry_rf_beacon_interval = int(rf_interval_seconds)
        return True

    def update_bitmask_telemetry_boot(self, rf_beacon_boot, uart_beacon_boot):
        """
        A function to update only the telemetry booth bitmask bits.

        :param rf_beacon_boot: HIGH = RF telemetry transmissions enabled on boot | LOW = RF telemetry transmissions
        disabled on boot
        :param uart_beacon_boot: HIGH = UART telemetry transmissions enabled on boot | LOW = RF telemetry transmissions
        disabled on boot

        :return: Nothing
        """
        bitmask = 0
        bitmask |= int(uart_beacon_boot) << 0
        bitmask |= int(rf_beacon_boot) << 1
        # self.basic_configuration_bitmask |= bitx << 2
        # self.basic_configuration_bitmask |= bitx << 3
        # self.basic_configuration_bitmask |= bitx << 4
        # self.basic_configuration_bitmask |= bitx << 5
        # self.basic_configuration_bitmask |= bitx << 6
        # self.basic_configuration_bitmask |= bitx << 7
        return bitmask

    def create_config_packet(self):
        """
        This function creates an entire Flash Info Segment D device configuration payload from the current values in
        the class object.

        :return: A complete Flash Info Segment D configuration payload as a string of bytes
        """
        # Create
        pkt_struct_config = struct.Struct('<B9s5B9x')
        config = pkt_struct_config.pack(self.basic_configuration_bitmask, self.basic_local_callsign,
                                        self.basic_local_callsign_len, self.basic_local_id, self.basic_gpio_p3_bitmask,
                                        self.basic_gpio_p4_bitmask, self.basic_gpio_p5_bitmask)

        pkt_struct_rf = struct.Struct('<3B1B21x')
        rf = pkt_struct_rf.pack(self.rf_default_boot_freq[0], self.rf_default_boot_freq[1],
                                self.rf_default_boot_freq[2], self.rf_PATable)

        pkt_struct_gps = struct.Struct('<9s1s10s1s8s1sB21x')
        gps = pkt_struct_gps.pack(self.gps_latitude, self.gps_latitude_dir, self.gps_longitude, self.gps_longitude_dir,
                                  self.gps_altitude, self.gps_altitude_units, self.gps_boot_bitmask)


        pkt_struct_telemetry = struct.Struct('<BHH10x')
        telem = pkt_struct_telemetry.pack(self.telemetry_boot_bitmask, self.telemetry_uart_beacon_interval,
                                          self.telemetry_rf_beacon_interval)

        # Return full configuration update packet payload (packet payload for configuration update is just the memory
        # allocation packet to be saved)
        return config + rf + gps + telem

    def parse_config_packet(self, packet):
        # Create parsing dictionary
        dict_config_parse = {}

        # Parse supplied config packet bytearray
        parsed_packet = self.config_pkt_struct_config.unpack(packet)

        dict_config_parse['configuration_bitmask'] = parsed_packet[0]
        dict_config_parse['local_callsign'] = parsed_packet[1]
        dict_config_parse['local_callsign_length'] = parsed_packet[2]
        dict_config_parse['local_callsign_id'] = parsed_packet[3]
        dict_config_parse['default_gpio_port_3_bitmask'] = parsed_packet[4]
        dict_config_parse['default_gpio_port_4_bitmask'] = parsed_packet[5]
        dict_config_parse['default_gpio_port_5_bitmask'] = parsed_packet[6]
        dict_config_parse['default_boot_freq_2'] = parsed_packet[7]
        dict_config_parse['default_boot_freq_1'] = parsed_packet[8]
        dict_config_parse['default_boot_freq_0'] = parsed_packet[9]
        dict_config_parse['default_rf_power'] = parsed_packet[10]
        dict_config_parse['default_gps_latitude'] = parsed_packet[11]
        dict_config_parse['default_gps_latitude_dir'] = parsed_packet[12]
        dict_config_parse['default_longitude'] = parsed_packet[13]
        dict_config_parse['default_longitude_dir'] = parsed_packet[14]
        dict_config_parse['default_altitude'] = parsed_packet[15]
        dict_config_parse['default_altitude_units'] = parsed_packet[16]
        dict_config_parse['gps_boot_bitmask'] = parsed_packet[17]
        dict_config_parse['telemetry_boot_bitmask'] = parsed_packet[18]
        dict_config_parse['default_telemetry_uart_beacon_interval'] = parsed_packet[19]
        dict_config_parse['default_telemetry_rf_beacon_interval'] = parsed_packet[20]

        # Return parsed packet
        return dict_config_parse
