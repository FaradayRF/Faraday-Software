from Basic_Proxy_IO import commandmodule
from Basic_Proxy_IO import gpioallocations

class faraday_commands(object):
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
        self.CMD_DEVICECONFIG = 255

    def CommandUpdateRFFreq(self, freq_mhz):
        """
        A predefined command to return a command packet containing the LOCAL faraday radio frequency in MHz.
        """
        packet = commandmodule.create_command_packet(self.CMD_UPDATEFREQUENCY, commandmodule.create_update_rf_frequency_packet(freq_mhz))
        return packet

    def CommandUARTUpdateNow(self):
        """
        A predefined command to return a command packet to command the LOCAL device to transmit its current telemetry packet #3 (normal telemetry) over UART.
        """
        packet = commandmodule.create_command_packet(self.CMD_LOCALTELEMNOW, commandmodule.create_local_telem_update_packet())
        return packet

    def CommandRFUpdateNow(self):
        """
        A predefined command to return a command packet to command the LOCAL device to transmit is current telemetry packet #3 (normal telemetry) over RF.
        """
        packet = commandmodule.create_command_packet(self.CMD_RFTELEMETRYNOW, commandmodule.create_rf_telem_update_packet())
        return packet

    def CommandUpdateUARTTelemetryInterval(self, interval):
        """
        A predefined command to return a command packet to update the LOCAL telemetry UART reporting interval without updating the default BOOT interval.
        """
        packet = commandmodule.create_command_packet(self.CMD_UPDATERAMPARAMETER, commandmodule.create_update_telemetry_interval_uart_packet(interval))
        return packet

    def CommandUpdateRFTelemetryInterval(self, interval):
        """
        A predefined command to return a command packet to update the LOCAL telemetry RF reporting interval without updating the default BOOT interval.
        """
        packet = commandmodule.create_command_packet(self.CMD_UPDATERAMPARAMETER, commandmodule.create_update_telemetry_interval_rf_packet(interval))
        return packet


    def CommandGPIOLED1On(self):
        """
        A predefined command to return a command packet to turn ON the LOCAL Faraday's LED #1 using the standard Faraday GPIO commanding packet.
        """
        packet = commandmodule.create_command_packet(self.CMD_GPIO, commandmodule.create_gpio_command_packet(int(gpioallocations.LED_1), 0, 0, 0, 0, 0 ))
        return packet

    def CommandGPIOLED1Off(self):
        """
        A predefined command to return a command packet to turn OFF the LOCAL Faraday's LED #1 using the standard Faraday GPIO commanding packet.
        """
        packet = commandmodule.create_command_packet(self.CMD_GPIO, commandmodule.create_gpio_command_packet(0, 0, 0, int(gpioallocations.LED_1), 0, 0 ))
        return packet

    def CommandGPIOLED2On(self):
        """
        A predefined command to return a command packet to turn ON the LOCAL Faraday's LED #2 using the standard Faraday GPIO commanding packet.
        """
        packet = commandmodule.create_command_packet(self.CMD_GPIO, commandmodule.create_gpio_command_packet(int(gpioallocations.LED_2), 0, 0, 0, 0, 0 ))
        return packet

    def CommandGPIOLED2Off(self):
        """
        A predefined command to return a command packet to turn OFF the LOCAL Faraday's LED #2 using the standard Faraday GPIO commanding packet.
        """
        packet = commandmodule.create_command_packet(self.CMD_GPIO, commandmodule.create_gpio_command_packet(0, 0, 0, int(gpioallocations.LED_2), 0, 0 ))
        return packet

    def CommandUpdatePATable(self, ucharPATable_Byte):
        """
        A predefined command to return a command packet to update the LOCAL Faraday RF Power Table settings without affecting the default BOOT power level.
        Note that a setting of 152 is the maximum output power, any number higher than 152 will be sent as a value of 152.
        """
        packet = commandmodule.create_command_packet(self.CMD_UPDATERFPOWER, commandmodule.create_update_rf_patable_packet(ucharPATable_Byte))
        return packet

    def CommandResetDeviceDebugFlash(self):
        """
        A predefined command to return a command packet that commands the LOCAL Faraday device to RESET it's "Flash Debug Information" to 0's.
        Flash debug information is engineering data that contains information about the devices boot, reset, and error statuses.
        This information is saved in non-volatile flash and will roll over to 0 if 255 is reached.
        """
        packet = commandmodule.create_command_packet(self.CMD_DEBUGFLASHRESET, commandmodule.create_reset_device_debug_flash_packet())
        return packet

    def CommandSendTelemDeviceDebugFlash(self):
        """
        A predefined command to return a command packet that causes LOCAL Faraday device to transmit it's "Flash Debug Information" over UART.
        Flash debug information is engineering data that contains information about the devices boot, reset, and error statuses.
        This information is saved in non-volatile flash and will roll over to 0 if 255 is reached.
        """
        packet = commandmodule.create_command_packet(self.CMD_DEBUGFLASHTELEMETRYNOW, commandmodule.create_send_telemetry_device_debug_flash())
        return packet

    def CommandSendTelemDeviceSystemSettings(self):
        """
        A predefined command to return a command packet to command the LOCAL Faraday device to transmit it's "Device System Settings" over UART.
        Device system settings contain information such as current radio frequency and power levels.
        """
        packet = commandmodule.create_command_packet(self.CMD_DEVICESETTINGSTELEMETRYNOW, commandmodule.create_send_telemetry_device_debug_flash())
        return packet

    def CommandHABActivateCutdownEvent(self):
        """
        A predefined command to return a command packet that commands a LOCAL Faraday device to perform activate it's High Altitutde Balloon application
        predefined cutdown event state machine sequence.
        """
        #Don't care what the payload is as long as it is at least 1 byte long
        packet = commandmodule.create_command_packet(self.CMD_APP_HAB_CUTDOWNNOW, commandmodule.create_send_telemetry_device_debug_flash())
        return packet

    def CommandHABResetAutoCutdownTimer(self):
        """
        A predefined command to return a command packet that commands a LOCAL Faraday device to RESET it's High Altitutde Balloon application
        automatic cutdown timer.
        """
        #Don't care what the payload is as long as it is at least 1 byte long
        packet = commandmodule.create_command_packet(self.CMD_APP_HAB_RESETAUTOCUTDOWNTIMER, commandmodule.create_send_telemetry_device_debug_flash())
        return packet

    def CommandHABDisableAutoCutdownTimer(self):
        """
        A predefined command to return a command packet that commands a LOCAL Faraday device to DISABLE it's High Altitutde Balloon application
        automatic cutdown timer.
        """
        #Don't care what the payload is as long as it is at least 1 byte long
        packet = commandmodule.create_command_packet(self.CMD_APP_HAB_DISABLEAUTOCUTDOWNTIMER, commandmodule.create_send_telemetry_device_debug_flash())
        return packet

    def CommandHABResetCutdownIdle(self):
        """
        A predefined command to return a command packet that commands a LOCAL Faraday device to set it's cutdown event state machine to IDLE = 0.
        This command is useful for either stopping an in-progress cutdown event or to reset the cutdown state machine
        to IDLE = 0 if the cutdown event has already occured and it is in IDLE = 255 state.
        """
        #Don't care what the payload is as long as it is at least 1 byte long
        packet = commandmodule.create_command_packet(self.CMD_APP_HAB_RESETCUTDOWNSTATEMACHINE, commandmodule.create_send_telemetry_device_debug_flash())
        return packet

    def CommandExperimentalRfPacketForward(self, data):
        """
        A predefined command to return a command packet that commands a LOCAL Faraday device to send the provided packet over a single RF packet.
        NOTE: The data must be equal or lesser length than the maximum RF packet payload!
        """
        packet = commandmodule.create_command_packet(self.CMD_RFPACKETFORWARD, data)
        return packet