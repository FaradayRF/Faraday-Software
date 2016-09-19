from ConfigParser import RawConfigParser
import os
import commandmodule

def NormalAbsConfigPath():
    return os.path.abspath('../faraday.ini')

def CreateConfigPacket():
    #Load from configuration file
    parser = RawConfigParser()
    parser.read('faraday.ini')
    print parser

    #Create a device configuration class (this allows rolling creation/edit of the configuration packet)
    deviceConfig = commandmodule.Device_Config_Class()

    #Update bitmask for basic configurations
    config_bitmask = deviceConfig.update_bitmask_configuration(True)
    #P3_bitmask = deviceConfig.update_bitmask_gpio_p3(0,0,0,0,1,0,0,0)
    #P4_bitmask = deviceConfig.update_bitmask_gpio_p4(0,0,0,1,0,0,0,0)
    #P5_bitmask = deviceConfig.update_bitmask_gpio_p5(0,0,0,1,0,0,0,0)
    P3_bitmask = int(parser.get('faradayio', 'p3_bitmask'))
    P4_bitmask = int(parser.get('faradayio', 'p4_bitmask'))
    P5_bitmask = int(parser.get('faradayio', 'p5_bitmask'))

    #need update for IO config
    callsign = str(parser.get('faraday', 'callsign'))
    nodeid = int(parser.get('faraday','nodeid'))
    bootfreq = float(parser.get('faraday','bootfreq'))
    powerconf = int(parser.get('faraday','powerconf'))
    uarttelemboot = int(parser.getboolean('faraday','uarttelemboot'))
    rftelemboot= bool(parser.getboolean('faraday','rftelemboot'))
    gpsboot = bool(parser.getboolean('faraday','gpsboot'))
    uartinterval = int(parser.get('faraday', 'uartinterval'))
    rfinterval = int(parser.get('faraday', 'rfinterval'))
    latitude = str(parser.get('location','latitude'))
    latdir = str(parser.get('location','latdir'))
    longitude = str(parser.get('location','longitude'))
    londir = str(parser.get('location','londir'))
    altitude = str(parser.get('location','altitude'))
    altunit = str(parser.get('location','altunit'))
    commandnum = int(parser.get('faraday', 'commandnum'))

    #Update the local basic information
    deviceConfig.update_basic(config_bitmask, callsign, nodeid,\
    P3_bitmask, P4_bitmask, P5_bitmask)

    #Update default RF configuration
    #159 is MAX PATable for Max output (5dBm into CC1190 in HGM)
    if(powerconf <= 159):
        deviceConfig.update_rf(bootfreq, powerconf)
    else:
        deviceConfig.update_rf(bootfreq, 159) #If input above max set to max

    #Update the GPS configuration
    gps_boot_bitmask = deviceConfig.update_bitmask_gps_boot(gpsboot)
    deviceConfig.update_gps(gps_boot_bitmask, latitude, latdir, longitude,\
    londir, altitude, altunit)

    #Update the Telemetry configuration
    telem_boot_bitmask = deviceConfig.update_bitmask_telemetry_boot(\
    rftelemboot, uarttelemboot)
    deviceConfig.update_telemetry(telem_boot_bitmask, uartinterval,\
    rfinterval)

    #Create the configuration command packet payload
    packet_config = deviceConfig.create_config_packet()

    #Create the full command packet with configuration packet as payload
    command_packet = commandmodule.create_command_packet(commandnum, packet_config)

    return command_packet