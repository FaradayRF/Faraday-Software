#imports
from Basic_Proxy_IO import faradaybasicproxyio
from Basic_Proxy_IO import faradaycommands
from Basic_Proxy_IO import telemetryparser
from Basic_Proxy_IO import faradayconfig

#Variables
local_device_callsign = 'kb1lqd'
local_device_node_id = 1

#Start the proxy server after configuring the configuration file correctly
#Setup a Faraday IO object
faraday_1 = faradaybasicproxyio.proxyio()
faraday_cmd = faradaycommands.faraday_commands()
faraday_parser = telemetryparser.TelemetryParse()

#########################################################################################
###Get current configuration information post configuration update.
#########################################################################################

#Display current device configuration prior to configuration flash update (Send UART telemetry update now command)
#Send the command to read the entire Flash Memory Info D allocations
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, faraday_cmd.CommandLocalSendReadDeviceConfig())
#Wait up to 1 second for the unit to respond to the command. NOTE: GETWait will return ALL packets received if more than 1 packet (likley not in THIS case)
rx_flashd_data = faraday_1.GETWait(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, 1, False) #Will block and wait for given time until a packet is recevied

#Decode the first packet in list from BASE 64 to a RAW bytesting
rx_flashd_decoded = faraday_1.DecodeJsonItemRaw(rx_flashd_data[0]['data'])
rx_flashd_decoded_extracted = faraday_parser.ExtractPaddedPacket(rx_flashd_decoded, faraday_parser.flash_config_info_d_struct_len)

print "\n--- Current Device Flash Device Callsign Information ---\n"
current_update_config = faraday_parser.UnpackConfigFlashD(rx_flashd_decoded_extracted, True)

#########################################################################################
###Update configuration using INI file as defined by Faraday device object and functions
#########################################################################################

#Create the Faraday Flash Configuration packet needed to updated the device from the INI configuration file.

#config_packet = faraday_device.create_config_packet() #Loads in INI file

#Transmit the configuration packet using the Faraday tools module POST Command function
#faraday_io_module.PostPortCMD(config_packet)


###########################################################################################
#####Get updated configuration information post configuration update.
###########################################################################################
##
##time.sleep(5) #Wait for Faraday to reboot
##
###Send the command to read the entire Flash Memory Info D allocations
##general_command.SendReadDeviceConfig()
##data_packet = faraday_io_module.GetPortJsonWait(2, 1, False) #Port 2 is the port that Faraday transmits back the data for a generic memory read.
##data_packet = data_packet[len(data_packet)-1]['data'] #Get last telemetry and print payload only in BASE64 (Last is most recent)
##decoded_data_packet = faraday_io_module.DecodeJsonItemRaw(data_packet)
##
##print "\n--- Updated Device Flash Device Callsign Information ---\n"
##post_update_config = telem_parser.UnpackConfigFlashD(decoded_data_packet, True)