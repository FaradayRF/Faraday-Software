
#-------------------------------------------------------------------------------
# Name:         debug.py
# Purpose:      Connects to a localhost proxy.py and automatically queries for
#               open application ports sending Faraday data and then requests
#               data for each open port and displays the decoded values (BASE64)
#
# Author:      Bryce Salmi
#
# Created:     03/04/2016
# Copyright:   (c) Bryce 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

# This script is a collection of common functions for Faraday Proxy interaction that abstracts the lower level function routines.

import json
import requests
import time
import threading
from collections import deque
import logging
import base64
import datetime
import CC430_Radio_Config
import struct
from ConfigParser import SafeConfigParser
import Command_Module
import gpio_allocation
import faraday
import parsing
from ConfigParser import SafeConfigParser

#setup proxy from configuration file
parser = SafeConfigParser()
parser.read('faraday.ini')
port = str(parser.getint('proxy','port'))

#Define constants
COMMAND_TRANSPORT_SERVICE_NUMBER = 2


def SendCommand(command_number, packet):
    """
    Send command will transmit the provided packet to the provided command "number" over the module defined UART "Service Port." Send Command utilizes the Farday
    proxy interface that implements a TCP socket FLASK interface.
    """
    #Create test configuration packet
    command_packet = Command_Module.create_command_packet(command_number, packet)
    #Encode into Base 64. This is needed due to the information being transmitted over a localhost stream and must be web "safe"
    b64cmd = base64.b64encode(command_packet)
    #Send command packet over localhost
    status = requests.post("http://127.0.0.1:" + port + "/faraday/"+ str(COMMAND_TRANSPORT_SERVICE_NUMBER) +"?cmd=%s" % b64cmd)
    return status


def send_cmd_echo(data):
    """
     A function that sends a command ECHO to Faraday. The payload will be sent back over the same port as CMD operation (2). Max payload is singled packet max length payload.
    """
    if(len(data)<123):
        test_packet = Command_Module.create_fixed_length_packet(data, 123)
        SendCommand(1, test_packet)
    else:
        print "Data too long for single packet"



def SendReadDeviceConfig():
    """
    A function that sends the command to read the device flash configuration from the local device.
    Note that this routine implements the memory read Faraday Python routine to read predefined
    Info memory.
    """
    packet = Command_Module.create_read_memory_packet(int('0x1800', 16), 121)
    SendCommand(2, packet)



def GetCommandData(service_port):
    """
    A function to return data received from Faraday on a port. This will return a list of all data packets received and decoded from BASE64.
    The function name is a bit misleading since ANY ports data can be retrieve not just the "Command port"
    """
    try:
        json_data = requests.get("http://127.0.0.1:" + port + "/faraday/"+ str(service_port))
        json_data_loaded = json.loads(json_data.text)
        data = []
        for i in range(0, len(json_data_loaded)):
            decoded_data = base64.b64decode(json_data_loaded[i]['data'])
            data.append(decoded_data)
        return data
    except:
        print "Fail to get"


##############
## Commands Summarized
##############

def SendCommand_Update_RF_Freq(freq_mhz):
    """
    A predefined command to update the LOCAL faraday radio frequency in MHz.
    """
    SendCommand(6, Command_Module.create_update_rf_frequency_packet(freq_mhz))

def SendCommand_Update_RAM_Callsign(callsign, device_id):
    """
    A predefined command to update the callsign / ID of the LOCAL faraday without updating the default boot callsign/ID.
    """
    SendCommand(4, Command_Module.create_update_callsign_packet(callsign, device_id))

def SendCommand_UART_Update_Now():
    """
    A predefined command to command the LOCAL device to transmit its current telemetry packet #3 (normal telemetry) over UART.
    """
    SendCommand(7, Command_Module.create_local_telem_update_packet())

def SendCommand_RF_Update_Now():
    """
    A predefined command to command the LOCAL device to transmit is current telemetry packet #3 (normal telemetry) over RF.
    """
    SendCommand(8, Command_Module.create_rf_telem_update_packet())

def SendCommand_Update_UART_Telemetry_Interval(interval):
    """
    A predefined command to update the LOCAL telemetry UART reporting interval without updating the default BOOT interval.
    """
    SendCommand(4, Command_Module.create_update_telemetry_interval_uart_packet(interval))

def SendCommand_Update_RF_Telemetry_Interval(interval):
    """
    A predefined command to update the LOCAL  telemetry RF reporting interval without updating the default BOOT interval.
    """
    SendCommand(4, Command_Module.create_update_telemetry_interval_rf_packet(interval))


def SendCommand_GPIO_LED_1_On():
    """
    A predefined command to turn ON the LOCAL  Faraday's LED #1 using the standard Faraday GPIO commanding packet.
    """
    SendCommand(5, Command_Module.create_gpio_command_packet(int(gpio_allocation.LED_1), 0, 0, 0, 0, 0 ))

def SendCommand_GPIO_LED_1_Off():
    """
    A predefined command to turn OFF the LOCAL  Faraday's LED #1 using the standard Faraday GPIO commanding packet.
    """
    SendCommand(5, Command_Module.create_gpio_command_packet(0, 0, 0, int(gpio_allocation.LED_1), 0, 0 ))

def SendCommand_GPIO_LED_2_On():
    """
    A predefined command to turn ON the LOCAL Faraday's LED #2 using the standard Faraday GPIO commanding packet.
    """
    SendCommand(5, Command_Module.create_gpio_command_packet(int(gpio_allocation.LED_2), 0, 0, 0, 0, 0 ))

def SendCommand_GPIO_LED_2_Off():
    """
    A predefined command to turn OFF the LOCAL Faraday's LED #2 using the standard Faraday GPIO commanding packet.
    """
    SendCommand(5, Command_Module.create_gpio_command_packet(0, 0, 0, int(gpio_allocation.LED_2), 0, 0 ))

def SendCommand_Update_PATable(ucharPATable_Byte):
    """
    A predefined command to update the LOCAL Faraday RF Power Table settings without affecting the default BOOT power level.
    Note that a setting of 152 is the maximum output power, any number higher than 152 will be sent as a value of 152.
    """
    SendCommand(10, Command_Module.create_update_rf_patable_packet(ucharPATable_Byte))

def SendCommand_Reset_Device_Debug_Flash():
    """
    A predefined command to command the LOCAL Faraday device to RESET it's "Flash Debug Information" to 0's.
    Flash debug information is engineering data that contains information about the devices boot, reset, and error statuses.
    This information is saved in non-volatile flash and will roll over to 0 if 255 is reached.
    """
    SendCommand(11, Command_Module.create_reset_device_debug_flash_packet())

def SendCommand_Send_Telem_Device_Debug_Flash():
    """
    A predefined command to command the LOCAL Faraday device to transmit it's "Flash Debug Information" over UART.
    Flash debug information is engineering data that contains information about the devices boot, reset, and error statuses.
    This information is saved in non-volatile flash and will roll over to 0 if 255 is reached.
    """
    SendCommand(12, Command_Module.create_send_telemetry_device_debug_flash()) #Don't care what the payload is

def SendCommand_Send_Telem_Device_System_Settings():
    """
    A predefined command to command the LOCAL Faraday device to transmit it's "Device System Settings" over UART.
    Device system settings contain information such as current radio frequency and power levels.
    """
    SendCommand(13, Command_Module.create_send_telemetry_device_debug_flash()) #Don't care what the payload is

def SendCommand_HAB_Activate_Cutdown_Event():
    """
    A predefined command that commands a LOCAL Faraday device to perform activate it's High Altitutde Balloon application
    predefined cutdown event state machine sequence.
    """
    SendCommand(14, Command_Module.create_send_telemetry_device_debug_flash()) #Don't care what the payload is

def SendCommand_HAB_Reset_Auto_Cutdown_Timer():
    """
    A predefined command that commands a LOCAL Faraday device to RESET it's High Altitutde Balloon application
    automatic cutdown timer.
    """
    SendCommand(15, Command_Module.create_send_telemetry_device_debug_flash()) #Don't care what the payload is

def SendCommand_HAB_Disable_Auto_Cutdown_Timer():
    """
    A predefined command that commands a LOCAL Faraday device to DISABLE it's High Altitutde Balloon application
    automatic cutdown timer.
    """
    SendCommand(16, Command_Module.create_send_telemetry_device_debug_flash()) #Don't care what the payload is

def SendCommand_HAB_Set_Cutdown_Idle():
    """
    A predefined command that commands a LOCAL Faraday device to set it's cutdown event state machine to IDLE = 0.
    This command is useful for either stopping an in-progress cutdown event or to reset the cutdown state machine
    to IDLE = 0 if the cutdown event has already occured and it is in IDLE = 255 state.
    """
    SendCommand(17, Command_Module.create_send_telemetry_device_debug_flash()) #Don't care what the payload is

##############
## RF Commands Examples
##############

def SendCommand_RF_Remote_Update_RAM_Callsign(dest_callsign, dest_id, new_callsign, new_id):
    """
    A predefined command to update the callsign / ID of the REMOTE faraday without updating the default boot callsign/ID.
    NOTE: This is dangerous to use as it will update the callsign of the REMOTE device and all future commands/telemetry will need
    to use this new callsign.
    """
    SendCommand(9, Command_Module.create_rf_command_packet(dest_callsign, dest_id, 4, Command_Module.create_update_callsign_packet(new_callsign, new_id)))

def SendCommand_RF_LED_1_On(dest_callsign, dest_id):
    """
    A predefined command to turn ON the REMOTE Faraday's LED #1 using the standard Faraday GPIO commanding packet.
    """
    SendCommand(9,Command_Module.create_rf_command_packet(dest_callsign, dest_id, 5, Command_Module.create_gpio_command_packet(int(gpio_allocation.LED_1), 0, 0, 0, 0, 0 )))

def SendCommand_RF_LED_1_Off(dest_callsign, dest_id):
    """
    A predefined command to turn OFF the REMOTE  Faraday's LED #1 using the standard Faraday GPIO commanding packet.
    """
    SendCommand(9,Command_Module.create_rf_command_packet(dest_callsign, dest_id, 5, Command_Module.create_gpio_command_packet(0, 0, 0, int(gpio_allocation.LED_1), 0, 0 )))

def SendCommand_RF_LED_2_On(dest_callsign, dest_id):
    """
    A predefined command to turn ON the REMOTE Faraday's LED #2 using the standard Faraday GPIO commanding packet.
    """
    SendCommand(9,Command_Module.create_rf_command_packet(dest_callsign, dest_id, 5, Command_Module.create_gpio_command_packet(int(gpio_allocation.LED_2), 0, 0, 0, 0, 0 )))

def SendCommand_RF_LED_2_Off(dest_callsign, dest_id):
    """
    A predefined command to turn OFF the REMOTE Faraday's LED #2 using the standard Faraday GPIO commanding packet.
    """
    SendCommand(9,Command_Module.create_rf_command_packet(dest_callsign, dest_id, 5, Command_Module.create_gpio_command_packet(0, 0, 0, int(gpio_allocation.LED_2), 0, 0 )))

def SendCommand_RF_Remote_UART_Update_Now(dest_callsign, dest_id):
    """
    A predefined command to command the REMOTE device to transmit its current telemetry packet #3 (normal telemetry) over UART.
    """
    SendCommand(9, Command_Module.create_rf_command_packet(dest_callsign, dest_id, 7, Command_Module.create_local_telem_update_packet()))

def SendCommand_RF_Remote_RF_Update_Now(dest_callsign, dest_id):
    """
    A predefined command to command the REMOTE device to transmit its current telemetry packet #3 (normal telemetry) over RF.
    """
    SendCommand(9, Command_Module.create_rf_command_packet(dest_callsign, dest_id, 8, Command_Module.create_rf_telem_update_packet()))

def SendCommand_RF_Remote_Update_UART_Telemetry_Interval(dest_callsign, dest_id, interval):
    """
    A predefined command to update the REMOTE telemetry UART reporting interval without updating the default BOOT interval.
    """
    SendCommand(9, Command_Module.create_rf_command_packet(dest_callsign, dest_id, 4, Command_Module.create_update_telemetry_interval_uart_packet(interval)))

def SendCommand_RF_Remote_Update_RF_Telemetry_Interval(dest_callsign, dest_id, interval):
    """
    A predefined command to update the REMOTE telemetry RF reporting interval without updating the default BOOT interval.
    """
    SendCommand(9, Command_Module.create_rf_command_packet(dest_callsign, dest_id, 4, Command_Module.create_update_telemetry_interval_rf_packet(interval)))

def SendCommand_RF_Remote_Update_RF_Freq(dest_callsign, dest_id, freq_mhz):
    """
    A predefined command to update the REMOTE faraday radio frequency in MHz.
    NOTE: This is a dangerous command since the REMOTE unit will change frequency after reception of the command.
    """
    SendCommand(9, Command_Module.create_rf_command_packet(dest_callsign, dest_id, 4, Command_Module.create_update_rf_frequency_packet(freq_mhz)))

def SendCommand_RF_HAB_Activate_Cutdown_Event(dest_callsign, dest_id):
    """
    A predefined command that commands a REMOTE Faraday device to perform activate it's High Altitutde Balloon application
    predefined cutdown event state machine sequence.
    """
    SendCommand(9, Command_Module.create_rf_command_packet(dest_callsign, dest_id, 14, Command_Module.create_local_telem_update_packet())) #Don't care what the payload is

def SendCommand_RF_HAB_Reset_Auto_Cutdown_Timer(dest_callsign, dest_id):
    """
    A predefined command that commands a REMOTE Faraday device to RESET it's High Altitutde Balloon application
    automatic cutdown timer.
    """
    SendCommand(9, Command_Module.create_rf_command_packet(dest_callsign, dest_id, 15, Command_Module.create_local_telem_update_packet())) #Don't care what the payload is

def SendCommand_RF_HAB_Disable_Auto_Cutdown_Timer(dest_callsign, dest_id):
    """
    A predefined command that commands a REMOTE Faraday device to DISABLE it's High Altitutde Balloon application
    automatic cutdown timer.
    """
    SendCommand(9, Command_Module.create_rf_command_packet(dest_callsign, dest_id, 16, Command_Module.create_local_telem_update_packet())) #Don't care what the payload is

def SendCommand_RF_HAB_Set_Cutdown_Idle(dest_callsign, dest_id):
    """
    A predefined command that commands a REMOTE Faraday device to set it's cutdown event state machine to IDLE = 0.
    This command is useful for either stopping an in-progress cutdown event or to reset the cutdown state machine
    to IDLE = 0 if the cutdown event has already occured and it is in IDLE = 255 state.
    """
    SendCommand(9, Command_Module.create_rf_command_packet(dest_callsign, dest_id, 17, Command_Module.create_local_telem_update_packet())) #Don't care what the payload is

if __name__ == '__main__':
    main()
