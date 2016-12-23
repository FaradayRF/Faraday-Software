from FaradayIO import commandmodule
from FaradayIO import gpioallocations

class faraday_commands(object):
    """
    An object containing command packet creation tools and predefined command generation functions.
    """
    def __init__(self):
        self.CMD_ECHO = 1
        self.CMD_READMEMORY = 2
        self.CMD_UPDATERAMPARAMETER = 4
        self.CMD_GPIO = 5
        self.CMD_UPDATEFREQUENCY = 6 #Can this be combined with UPDATERAMPARAMETER?
        self.CMD_LOCALTELEMNOW = 7
        self.CMD_RFTELEMETRYNOW = 8
        self.CMD_SENDRFCOMMAND = 9
        self.CMD_UPDATERFPOWER = 10
        self.CMD_DEBUGFLASHRESET = 11
        self.CMD_DEBUGFLASHTELEMETRYNOW = 12
        self.CMD_DEVICESETTINGSTELEMETRYNOW = 13
        self.CMD_APP_HAB_CUTDOWNNOW = 14
        self.CMD_APP_HAB_RESETAUTOCUTDOWNTIMER = 15
        self.CMD_APP_HAB_DISABLEAUTOCUTDOWNTIMER = 16
        self.CMD_APP_HAB_RESETCUTDOWNSTATEMACHINE = 17
        self.CMD_RFPACKETFORWARD = 18
        self.CMD_DEVICECONFIGFACTORYRESET = 254
        self.CMD_DEVICECONFIG = 255

        #Flash Info D Constants
        self.FLASHD_MEMORY_LOC = 0x1800
        self.FLASHD_LENGTH = 121

    def CommandLocal(self, command_number, command_packet):
        """
        A predefined function that returns a raw command application DATAGRAM that will cause the supplied command to be executed on a local device.

        :param command_number: Command application command identification number (Identifies a command/command type using 0-255)
        :param command_packet: Pass a pre-generated packet as defined by the intended command.

        :Return: Returns the complete generated packet as a string of bytes.

        :Example:

        >>> faraday_cmd = faradaycommands.faraday_commands()
        >>> packet = faraday_cmd.CommandLocal(faraday_cmd.CMD_UPDATERFPOWER, faradaycommands.commandmodule.create_update_rf_patable_packet(50))
        """
        packet = commandmodule.create_command_datagram(command_number, command_packet)
        return packet

    def CommandRf(self, remote_callsign, remote_node_id, command_number, command_packet):
        """
        A predefined function that returns a raw command application DATAGRAM that will cause the supplied command to be executed on a remote (RF) device. This is basically and local command inside the payload of a command to transmit a command to a specific RF unit.

        :param remote_callsign: The callsign of the remote target Faraday device
        :param remote_node_id: The ID number (0-255) of the remote target Faraday device.
        :param command_number: Command application command identification number (Identifies a command/command type using 0-255)
        :param command_packet: Pass a pre-generated packet as defined by the intended command.

        :Return: Returns the complete generated packet as a string of bytes.

        :Example:

        >>> faraday_cmd = faradaycommands.faraday_commands()
        >>> packet = faraday_cmd.CommandRf("KB1LQD", 1, faraday_cmd.CMD_GPIO, faradaycommands.commandmodule.create_gpio_command_packet(faradaycommands.gpioallocations.LED_1, 0,0,0,0,0))
        """
        packet = commandmodule.create_rf_command_datagram(remote_callsign, remote_node_id, command_number, command_packet)
        return packet

    ###############################
    ## Predefined LOCAL Commands
    ###############################

    def CommandLocalUpdateRFFreq(self, freq_mhz):
        """
        A predefined command to return a command complete DATAGRAM and packet that will command a change in the LOCAL faraday radio frequency.

        :param freq_mhz: The frequency in MHz as an integer or float.

        :Return: Returns the complete generated packet as a string of bytes.
        """
        packet = commandmodule.create_command_datagram(self.CMD_UPDATEFREQUENCY, commandmodule.create_update_rf_frequency_packet(freq_mhz))
        return packet

    def CommandLocalUARTFaradayTelemetry(self):
        """
        A predefined command to return a complete command datagram and packet to command the LOCAL device to transmit its current telemetry packet #3 (normal telemetry) over UART.

        :Return: Returns the complete generated packet as a string of bytes.
        """
        packet = commandmodule.create_command_datagram(self.CMD_LOCALTELEMNOW, commandmodule.create_local_telem_update_packet())
        return packet

    def CommandLocalRFUpdateNow(self):
        """
        A predefined command to return a complete command datagram and command packet to command the LOCAL device to transmit is current telemetry packet #3 (normal telemetry) over RF.

        :Return: Returns the complete generated packet as a string of bytes.
        """
        packet = commandmodule.create_command_datagram(self.CMD_RFTELEMETRYNOW, commandmodule.create_rf_telem_update_packet())
        return packet

    def CommandLocalUpdateUARTTelemetryInterval(self, interval):
        """
        A predefined command to return a complete command datagram and command packet to update the LOCAL telemetry UART reporting interval without updating the default BOOT interval.

        :param interval: Time interval in seconds (Is a 2 byte Integer: 0-65535)

        :Return: Returns the complete generated packet as a string of bytes.
        """
        packet = commandmodule.create_command_datagram(self.CMD_UPDATERAMPARAMETER, commandmodule.create_update_telemetry_interval_uart_packet(interval))
        return packet

    def CommandLocalUpdateRFTelemetryInterval(self, interval):
        """
        A predefined command to return a complete command datagram and command packet to update the LOCAL telemetry RF reporting interval without updating the default BOOT interval.

        :param interval: Time interval in seconds (Is a 2 byte Integer: 0-65535)

        :Return: Returns the complete generated packet as a string of bytes.

        """
        packet = commandmodule.create_command_datagram(self.CMD_UPDATERAMPARAMETER, commandmodule.create_update_telemetry_interval_rf_packet(interval))
        return packet


    def CommandLocalGPIOLED1On(self):
        """
        A predefined command to return a complete datagram and command packet to turn ON the LOCAL Faraday's LED #1 using the standard Faraday GPIO commanding packet.

        :Return: Returns the complete generated packet as a string of bytes.

        """
        packet = commandmodule.create_command_datagram(self.CMD_GPIO, commandmodule.create_gpio_command_packet(int(gpioallocations.LED_1), 0, 0, 0, 0, 0 ))
        return packet

    def CommandLocalGPIOLED1Off(self):
        """
        A predefined command to return a complete datagram and command packet to turn OFF the LOCAL Faraday's LED #1 using the standard Faraday GPIO commanding packet.

        :Return: Returns the complete generated packet as a string of bytes.

        """
        packet = commandmodule.create_command_datagram(self.CMD_GPIO, commandmodule.create_gpio_command_packet(0, 0, 0, int(gpioallocations.LED_1), 0, 0 ))
        return packet

    def CommandLocalGPIOLED2On(self):
        """
        A predefined command to return a complete datagram and command packet to turn ON the LOCAL Faraday's LED #2 using the standard Faraday GPIO commanding packet.

        :Return: Returns the complete generated packet as a string of bytes.

        """
        packet = commandmodule.create_command_datagram(self.CMD_GPIO, commandmodule.create_gpio_command_packet(int(gpioallocations.LED_2), 0, 0, 0, 0, 0 ))
        return packet

    def CommandLocalGPIOLED2Off(self):
        """
        A predefined command to return a complete datagram and command packet to turn OFF the LOCAL Faraday's LED #2 using the standard Faraday GPIO commanding packet.

        :Return: Returns the complete generated packet as a string of bytes.

        """
        packet = commandmodule.create_command_datagram(self.CMD_GPIO, commandmodule.create_gpio_command_packet(0, 0, 0, int(gpioallocations.LED_2), 0, 0 ))
        return packet

    def CommandLocalUpdatePATable(self, ucharPATable_Byte):
        """
        A predefined command to return a a complete datagram and command packet to update the LOCAL Faraday RF Power Table settings without affecting the default BOOT power level.
        Note that a setting of 152 is the maximum output power, any number higher than 152 will be sent as a value of 152.

        :param ucharPATable_Byte: A single byte value for the PA table RF power setting on the CC430

        :Return: Returns the complete generated packet as a string of bytes.

        """
        packet = commandmodule.create_command_datagram(self.CMD_UPDATERFPOWER, commandmodule.create_update_rf_patable_packet(ucharPATable_Byte))
        return packet

    def CommandLocalResetDeviceDebugFlash(self):
        """
        A predefined command to return a complete datagram and command packet that commands the LOCAL Faraday device to RESET it's "Flash Debug Information" to 0's.

        Flash debug information is engineering data that contains information about the devices boot, reset, and error statuses.
        This information is saved in non-volatile flash and will roll over to 0 if 255 is reached.

        :Return: Returns the complete generated packet as a string of bytes.

        """
        packet = commandmodule.create_command_datagram(self.CMD_DEBUGFLASHRESET, commandmodule.create_reset_device_debug_flash_packet())
        return packet

    def CommandLocalSendTelemDeviceDebugFlash(self):
        """
        A predefined command to return a complete datagram and command packet that causes LOCAL Faraday device to transmit it's "Flash Debug Information" over UART.

        Flash debug information is engineering data that contains information about the devices boot, reset, and error statuses.
        This information is saved in non-volatile flash and will roll over to 0 if 255 is reached.

        :Return: Returns the complete generated packet as a string of bytes.

        """
        packet = commandmodule.create_command_datagram(self.CMD_DEBUGFLASHTELEMETRYNOW, commandmodule.create_send_telemetry_device_debug_flash())
        return packet

    def CommandLocalSendTelemDeviceSystemSettings(self):
        """
        A predefined command to return a complete datagram and command packet to command the LOCAL Faraday device to transmit it's "Device System Settings" over UART.

        Device system settings contain information such as current radio frequency and power levels.

        :Return: Returns the complete generated packet as a string of bytes.

        """
        packet = commandmodule.create_command_datagram(self.CMD_DEVICESETTINGSTELEMETRYNOW, commandmodule.create_send_telemetry_device_debug_flash())
        return packet

    def CommandLocalFactoryResetConfiguration(self):
        """
        A predefined commanmd that invokes the function that resets the Faraday device information configuration (i.e.
        callsign, boot default settings, etc...) to a factory default configuration. This is the configuration used
        during first boot of a new unit.

        :Return: Returns the complete generated packet as a string of bytes
        """
        packet = commandmodule.create_command_datagram(self.CMD_DEVICECONFIGFACTORYRESET, commandmodule.create_empty_command_packet())
        return packet


    def CommandLocalHABActivateCutdownEvent(self):
        """
        A predefined command to return a complete command datagram and  command packet that commands a LOCAL Faraday device to perform activate it's High Altitutde Balloon application
        predefined cutdown event state machine sequence.

        :Return: Returns the complete generated packet as a string of bytes.

        """
        #Don't care what the payload is as long as it is at least 1 byte long
        packet = commandmodule.create_command_datagram(self.CMD_APP_HAB_CUTDOWNNOW, commandmodule.create_send_telemetry_device_debug_flash())
        return packet

    def CommandLocalHABResetAutoCutdownTimer(self):
        """
        A predefined command to return a complete command datagram and command packet that commands a LOCAL Faraday device to RESET it's High Altitutde Balloon application
        automatic cutdown timer.

        :Return: Returns the complete generated packet as a string of bytes.

        """
        #Don't care what the payload is as long as it is at least 1 byte long
        packet = commandmodule.create_command_datagram(self.CMD_APP_HAB_RESETAUTOCUTDOWNTIMER, commandmodule.create_send_telemetry_device_debug_flash())
        return packet

    def CommandLocalHABDisableAutoCutdownTimer(self):
        """
        A predefined command to return a complete command datagram and command packet that commands a LOCAL Faraday device to DISABLE it's High Altitutde Balloon application
        automatic cutdown timer.

        :Return: Returns the complete generated packet as a string of bytes.

        """
        #Don't care what the payload is as long as it is at least 1 byte long
        packet = commandmodule.create_command_datagram(self.CMD_APP_HAB_DISABLEAUTOCUTDOWNTIMER, commandmodule.create_send_telemetry_device_debug_flash())
        return packet

    def CommandLocalHABResetCutdownIdle(self):
        """
        A predefined command to return a complete command datagram and command packet that commands a LOCAL Faraday device to set it's cutdown event state machine to IDLE = 0.

        This command is useful for either stopping an in-progress cutdown event or to reset the cutdown state machine
        to IDLE = 0 if the cutdown event has already occured and it is in IDLE = 255 state.

        :Return: Returns the complete generated packet as a string of bytes.

        """
        #Don't care what the payload is as long as it is at least 1 byte long
        packet = commandmodule.create_command_datagram(self.CMD_APP_HAB_RESETCUTDOWNSTATEMACHINE, commandmodule.create_send_telemetry_device_debug_flash())
        return packet

    def CommandLocalExperimentalRfPacketForward(self, remote_callsign, remote_node_id, data):
        """
        A predefined command to return a complete command datagram and command packet that commands a LOCAL Faraday device to send the provided packet over a single RF packet.

        :param remote_callsign: The callsign of the remote target Faraday device
        :param remote_node_id: The ID number (0-255) of the remote target Faraday device.
        :param data: The data payload (Text, packet, etc...) that is to transmitted to the remote Faraday device

        :Return: Returns the complete generated packet as a string of bytes.


        .. Note:: The data must be equal or lesser length than the maximum RF packet payload!

        :Example:

        >>> command_packet = faraday_cmd.CommandLocalExperimentalRfPacketForward("KB1LQD", 1, "This is a test message")

        """
        packet = commandmodule.create_command_datagram(self.CMD_RFPACKETFORWARD, commandmodule.CreatePacketMsgExperimental(0, remote_callsign, remote_node_id, len(data), data))
        return packet

    def CommandLocalGPIO(self, p3_bitmask_on, p4_bitmask_on, p5_bitmask_on, p3_bitmask_off, p4_bitmask_off, p5_bitmask_off):
        """
        A predefined command to return a complete command datagram and command packet to create a generic GPIO ON/OFF bitmask command.

        :param p3_bitmask_on: A 1 byte bitmask for PORT 3 GPIO that if bit HIGH it will toggle the corresponding GPIO HIGH. If bit is LOW it will have no affect on the corresponding GPIO.
        :param p4_bitmask_on: A 1 byte bitmask for PORT 4 GPIO that if bit HIGH it will toggle the corresponding GPIO HIGH. If bit is LOW it will have no affect on the corresponding GPIO.
        :param p5_bitmask_on: A 1 byte bitmask for PORT 5 GPIO that if bit HIGH it will toggle the corresponding GPIO HIGH. If bit is LOW it will have no affect on the corresponding GPIO.
        :param p3_bitmask_off: A 1 byte bitmask for PORT 3 GPIO that if bit HIGH it will toggle the corresponding GPIO LOW. If bit is LOW it will have no affect on the corresponding GPIO.
        :param p4_bitmask_off: A 1 byte bitmask for PORT 4 GPIO that if bit HIGH it will toggle the corresponding GPIO LOW. If bit is LOW it will have no affect on the corresponding GPIO.
        :param p5_bitmask_off: A 1 byte bitmask for PORT 5 GPIO that if bit HIGH it will toggle the corresponding GPIO LOW. If bit is LOW it will have no affect on the corresponding GPIO.

        :Return: Returns the complete generated packet as a string of bytes.


        :Example:

        >>> faraday_cmd = faradaycommands.faraday_commands()
        #Turn ON LED 1
        >>> command_packet = faraday_cmd.CommandLocalGPIO(faradaycommands.gpioallocations.LED_1, 0,0,0,0,0)
        #Turn OFF LED 1
        >>> command_packet = faraday_cmd.CommandLocalGPIO(0, 0,0,faradaycommands.gpioallocations.LED_1,0,0)
        #Turn ON LED 1 & LED 2
        >>> command_packet = faraday_cmd.CommandLocalGPIO(faradaycommands.gpioallocations.LED_1 | faradaycommands.gpioallocations.LED_2, 0,0,0,0,0)

        """
        packet = commandmodule.create_command_datagram(self.CMD_GPIO, commandmodule.create_gpio_command_packet(p3_bitmask_on, p4_bitmask_on, p5_bitmask_on, p3_bitmask_off, p4_bitmask_off, p5_bitmask_off))
        return packet

    def CommandLocalSendReadDeviceConfig(self):
        """
        A function returns a complete command datagram and command packet to read the device flash configuration from the local device. This function implements the memory read Faraday Python routine to read
        memory addresses with predefined arguments.

        :Return: Returns the complete generated packet as a string of bytes.

        """
        packet = commandmodule.create_command_datagram(self.CMD_READMEMORY, commandmodule.create_read_memory_packet(self.FLASHD_MEMORY_LOC, self.FLASHD_LENGTH))
        return packet


    ###############################
    ## Predefined RF Commands
    ###############################
    def CommandRemoteUARTUpdateNow(self, remote_callsign, remote_node_id):
        """
        A predefined command to return a complete datagram and command packet to command the REMOTE (RF) device to transmit its current telemetry packet #3 (normal telemetry) over UART.

        :param remote_callsign: The callsign of the remote target Faraday device
        :param remote_node_id: The ID number (0-255) of the remote target Faraday device.

        :Return: Returns the complete generated packet as a string of bytes.

        """
        packet = commandmodule.create_rf_command_datagram(remote_callsign, remote_node_id, self.CMD_LOCALTELEMNOW, commandmodule.create_local_telem_update_packet())
        return packet

    def CommandRemoteRFUpdateNow(self, remote_callsign, remote_node_id):
        """
        A predefined command to return a complete datagram and command packet to command the REMOTE (RF) device to transmit is current telemetry packet #3 (normal telemetry) over RF.

        :param remote_callsign: The callsign of the remote target Faraday device
        :param remote_node_id: The ID number (0-255) of the remote target Faraday device.

        :Return: Returns the complete generated packet as a string of bytes.

        """
        packet = commandmodule.create_rf_command_datagram(remote_callsign, remote_node_id, self.CMD_RFTELEMETRYNOW, commandmodule.create_rf_telem_update_packet())
        return packet


    def CommandRemoteGPIOLED1On(self, remote_callsign, remote_node_id):
        """
        A predefined command to return a complete datagram and command packet to turn ON the REMOTE (RF) Faraday's LED #1 using the standard Faraday GPIO commanding packet.

        :param remote_callsign: The callsign of the remote target Faraday device
        :param remote_node_id: The ID number (0-255) of the remote target Faraday device.

        :Return: Returns the complete generated packet as a string of bytes.

        """
        packet = commandmodule.create_rf_command_datagram(remote_callsign, remote_node_id, self.CMD_GPIO, commandmodule.create_gpio_command_packet(int(gpioallocations.LED_1), 0, 0, 0, 0, 0 ))
        return packet

    def CommandRemoteGPIOLED1Off(self, remote_callsign, remote_node_id):
        """
        A predefined command to return a complete datagram and command packet to turn OFF the REMOTE (RF) Faraday's LED #1 using the standard Faraday GPIO commanding packet.

        :param remote_callsign: The callsign of the remote target Faraday device
        :param remote_node_id: The ID number (0-255) of the remote target Faraday device.

        :Return: Returns the complete generated packet as a string of bytes.

        """
        packet = commandmodule.create_rf_command_datagram(remote_callsign, remote_node_id, self.CMD_GPIO, commandmodule.create_gpio_command_packet(0, 0, 0, int(gpioallocations.LED_1), 0, 0 ))
        return packet

    def CommandRemoteGPIOLED2On(self, remote_callsign, remote_node_id):
        """
        A predefined command to return a complete datagram and command packet to turn ON the REMOTE (RF) Faraday's LED #2 using the standard Faraday GPIO commanding packet.

        :param remote_callsign: The callsign of the remote target Faraday device
        :param remote_node_id: The ID number (0-255) of the remote target Faraday device.

        :Return: Returns the complete generated packet as a string of bytes.

        """
        packet = commandmodule.create_rf_command_datagram(remote_callsign, remote_node_id, self.CMD_GPIO, commandmodule.create_gpio_command_packet(int(gpioallocations.LED_2), 0, 0, 0, 0, 0 ))
        return packet

    def CommandRemoteGPIOLED2Off(self, remote_callsign, remote_node_id):
        """
        A predefined command to return a complete datagram and command packet to turn OFF the REMOTE (RF) Faraday's LED #2 using the standard Faraday GPIO commanding packet.

        :param remote_callsign: The callsign of the remote target Faraday device
        :param remote_node_id: The ID number (0-255) of the remote target Faraday device.

        :Return: Returns the complete generated packet as a string of bytes.

        """
        packet = commandmodule.create_rf_command_datagram(remote_callsign, remote_node_id, self.CMD_GPIO, commandmodule.create_gpio_command_packet(0, 0, 0, int(gpioallocations.LED_2), 0, 0 ))
        return packet


    def CommandRemoteHABActivateCutdownEvent(self, remote_callsign, remote_node_id):
        """
        A predefined command to return a complete datagram and command packet that commands a REMOTE (RF) Faraday device to perform activate it's High Altitutde Balloon application
        predefined cutdown event state machine sequence.

        :param remote_callsign: The callsign of the remote target Faraday device
        :param remote_node_id: The ID number (0-255) of the remote target Faraday device.

        :Return: Returns the complete generated packet as a string of bytes.

        """
        #Don't care what the payload is as long as it is at least 1 byte long
        packet = commandmodule.create_rf_command_datagram(remote_callsign, remote_node_id, self.CMD_APP_HAB_CUTDOWNNOW, commandmodule.create_send_telemetry_device_debug_flash())
        return packet

    def CommandRemoteHABResetAutoCutdownTimer(self, remote_callsign, remote_node_id):
        """
        A predefined command to return a complete datagram and command packet that commands a REMOTE (RF) Faraday device to RESET it's High Altitutde Balloon application
        automatic cutdown timer.

        :param remote_callsign: The callsign of the remote target Faraday device
        :param remote_node_id: The ID number (0-255) of the remote target Faraday device.

        :Return: Returns the complete generated packet as a string of bytes.

        """
        #Don't care what the payload is as long as it is at least 1 byte long
        packet = commandmodule.create_rf_command_datagram(remote_callsign, remote_node_id, self.CMD_APP_HAB_RESETAUTOCUTDOWNTIMER, commandmodule.create_send_telemetry_device_debug_flash())
        return packet

    def CommandRemoteHABDisableAutoCutdownTimer(self, remote_callsign, remote_node_id):
        """
        A predefined command to return a complete datagram and command packet that commands a REMOTE (RF) Faraday device to DISABLE it's High Altitutde Balloon application
        automatic cutdown timer.

        :param remote_callsign: The callsign of the remote target Faraday device
        :param remote_node_id: The ID number (0-255) of the remote target Faraday device.

        :Return: Returns the complete generated packet as a string of bytes.

        """
        #Don't care what the payload is as long as it is at least 1 byte long
        packet = commandmodule.create_rf_command_datagram(remote_callsign, remote_node_id, self.CMD_APP_HAB_DISABLEAUTOCUTDOWNTIMER, commandmodule.create_send_telemetry_device_debug_flash())
        return packet

    def CommandRemoteHABResetCutdownIdle(self, remote_callsign, remote_node_id):
        """
        A predefined command to return a complete datagram and command packet that commands a REMOTE (RF) Faraday device to set it's cutdown event state machine to IDLE = 0.
        This command is useful for either stopping an in-progress cutdown event or to reset the cutdown state machine
        to IDLE = 0 if the cutdown event has already occured and it is in IDLE = 255 state.

        :param remote_callsign: The callsign of the remote target Faraday device
        :param remote_node_id: The ID number (0-255) of the remote target Faraday device.

        :Return: Returns the complete generated packet as a string of bytes.

        """
        #Don't care what the payload is as long as it is at least 1 byte long
        packet = commandmodule.create_rf_command_datagram(remote_callsign, remote_node_id, self.CMD_APP_HAB_RESETCUTDOWNSTATEMACHINE, commandmodule.create_send_telemetry_device_debug_flash())
        return packet


    def CommandRemoteGPIO(self, remote_callsign, remote_node_id, p3_bitmask_on, p4_bitmask_on, p5_bitmask_on, p3_bitmask_off, p4_bitmask_off, p5_bitmask_off):
        """
        A predefined command to return a complete datagram and command packet to command ALL GPIO's avaailable on a REMOTE (RF) Faraday device (see documentation).

        .. Note:: Please see the Faraday documentation on GPIO for more information about the GPIO bitmask assignments.

        :param remote_callsign: The callsign of the remote target Faraday device
        :param remote_node_id: The ID number (0-255) of the remote target Faraday device.
        :param p3_bitmask_on: A 1 byte bitmask for PORT 3 GPIO that if bit HIGH it will toggle the corresponding GPIO HIGH. If bit is LOW it will have no affect on the corresponding GPIO.
        :param p4_bitmask_on: A 1 byte bitmask for PORT 4 GPIO that if bit HIGH it will toggle the corresponding GPIO HIGH. If bit is LOW it will have no affect on the corresponding GPIO.
        :param p5_bitmask_on: A 1 byte bitmask for PORT 5 GPIO that if bit HIGH it will toggle the corresponding GPIO HIGH. If bit is LOW it will have no affect on the corresponding GPIO.
        :param p3_bitmask_off: A 1 byte bitmask for PORT 3 GPIO that if bit HIGH it will toggle the corresponding GPIO LOW. If bit is LOW it will have no affect on the corresponding GPIO.
        :param p4_bitmask_off: A 1 byte bitmask for PORT 4 GPIO that if bit HIGH it will toggle the corresponding GPIO LOW. If bit is LOW it will have no affect on the corresponding GPIO.
        :param p5_bitmask_off: A 1 byte bitmask for PORT 5 GPIO that if bit HIGH it will toggle the corresponding GPIO LOW. If bit is LOW it will have no affect on the corresponding GPIO.

        :Return: Returns the complete generated packet as a string of bytes.


        :Example:

        >>> faraday_cmd = faradaycommands.faraday_commands()
        #Turn ON LED 1
        >>> command_packet = faraday_cmd.CommandRemoteGPIO("KB1LQD", 1, faradaycommands.gpioallocations.LED_1, 0,0,0,0,0)
        #Turn OFF LED 1
        >>> command_packet = faraday_cmd.CommandRemoteGPIO("KB1LQD", 1, 0, 0,0,faradaycommands.gpioallocations.LED_1,0,0)
        #Turn ON LED 1 & LED 2
        >>> command_packet = faraday_cmd.CommandRemoteGPIO("KB1LQD", 1, faradaycommands.gpioallocations.LED_1 | faradaycommands.gpioallocations.LED_2, 0,0,0,0,0)

        """
        packet = commandmodule.create_rf_command_datagram(remote_callsign, remote_node_id, self.CMD_GPIO, commandmodule.create_gpio_command_packet(p3_bitmask_on, p4_bitmask_on, p5_bitmask_on, p3_bitmask_off, p4_bitmask_off, p5_bitmask_off))
        return packet
