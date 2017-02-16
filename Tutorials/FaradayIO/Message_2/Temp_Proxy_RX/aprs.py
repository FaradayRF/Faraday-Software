#-------------------------------------------------------------------------------
# Name:        aprs.py
# Purpose:
#
# Author:      Bryce
#
# Created:     19/06/2016
# Copyright:   (c) Bryce 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys
import logging
import logging.config
import time
import json
import requests
import os
import socket
import threading
import errno

def connectAPRSIS():
	print "Connecting to APRS-IS Server...\r"
	aprs_server = 'second.aprs.net'
	aprs_port = 20157
	aprssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	while True:
		try:
			aprssock.connect((aprs_server, aprs_port))
			logon_string = 'user' + ' ' + 'KB1LQC' + ' ' +  'pass' + ' ' + str(22703) + ' vers "FaradayRF APRS-IS script" \r'
			aprssock.sendall(logon_string)

		except socket.error as e:
			print e

		else:
			print "Connected to %s on port %d!" % (aprs_server,aprs_port)
			return aprssock
			break
		time.sleep(10) #Try to reconnect every 10 seconds

def getCurrentStations():
    currentStations = requests.get("http://127.0.0.1/faraday/stations").text
    return json.loads(currentStations)

def getStationData(stations):
    data = []
    for station in stations:
        payload = {'callsign': station["callsign"], 'nodeid': station["id"], 'limit': 1}
        stationData = requests.get("http://127.0.0.1/faraday/telemetry", params=payload).text
        data.append(json.loads(stationData))
    return data

def aprsPosition(data):
    for station in data:
        station = station[0]

        if (station["gpsfix"] == 1) or (station["gpsfix"] == 2):
            # Extract stations
            node = station["callsign"] + "-" + str(station["id"])
            destNode = station["destcallsign"] + "-" + str(station["destid"])

            #Extract node GPS data suitable for APRS-IS use
            dmlat = "%.2f" % round(station["latdec"],2)
            dmlon = "%.2f" % round(station["londec"],2)
            latdeg = str(station["latdeg"])
            londeg = str(station["londeg"])
            latdir = station["latdir"]
            londir = station['londir']
            rawaltitude = str(round(station["altitude"],0)).split('.')
            altitude = rawaltitude[0].zfill(6)
            rawspeed = str(round(station["speed"],0)).split('.')
            speed = rawspeed[0].zfill(3)

            aprsposition = '=' + latdeg + dmlat + latdir + '/' + londeg + dmlon + londir

            if station["aprf"] == 1:
                positionString = node + '>GPSFDY,' + 'qAR,' + destNode + ':' + aprsposition + '[' + '.../' + speed + '/A=' + altitude + 'FaradayRF Modem' + '\r'
            else:
                positionString = node + '>GPSFDY,' + ':' + aprsposition + '[' + '.../' + speed + '/A=' + altitude + 'FaradayRF Modem' + '\r'
            print positionString
            aprs = connectAPRSIS()
            aprs.sendall(positionString)
            aprs.close()

def aprsTelemetry(telemSequence,data):
    for station in data:
        station = station[0]

        if (station["gpsfix"] == 1) or (station["gpsfix"] == 2): #might not actually need this for telemetry!
            # Extract stations
            node = station["callsign"] + "-" + str(station["id"])
            destNode = station["destcallsign"] + "-" + str(station["destid"])

            #Extract GPIO data
            gpio = bin(station["gpio1"])[2:].zfill(8) #get on-board IO state (mosfet, button, etc)


            # Make telemetry string from supplied data
            if station["aprf"] == 1:
                telemString = node + '>GPSFDY,' + 'qAR,' + destNode + ':T#' + str(telemSequence).zfill(3) + ',' + str(station["adc0"]/16).zfill(3) + ',' + str(station["adc1"]/16).zfill(3) + ',' + str(station["adc2"]/16).zfill(3) + ',' + str(station["adc7"]/16).zfill(3) + ',' + str(station["adc8"]/16).zfill(3) + ',' + gpio + '\r'
            else:
                telemString = node + '>GPSFDY' + ':T#' + str(telemSequence).zfill(3) + ',' + str(station["adc0"]/16).zfill(3) + ',' + str(station["adc1"]/16).zfill(3) + ',' + str(station["adc2"]/16).zfill(3) + ',' + str(station["adc7"]/16).zfill(3) + ',' + str(station["adc8"]/16).zfill(3) + ',' + gpio + '\r'
            print telemString
            aprs = connectAPRSIS()
            aprs.sendall(telemString)
            aprs.close()
    telemSequence += 1
    return telemSequence

def aprsLabels(data):
    """Specifies the units/labels of channels for APRS telemetry and sends them to APRS-IS"""
    #temporary
    unit0 = "CNT"
    unit1 = "CNT"
    unit2 = "CNT"
    unit3 = "CNT"
    unit4 = "CNT"
    bLabel0 = "IO"
    bLabel1 = "IO"
    bLabel2 = "IO"
    bLabel3 = "IO"
    bLabel4 = "IO"
    bLabel5 = "IO"
    bLabel6 = "IO"
    bLabel7 = "IO"
    for station in data:
        station = station[0]
        if (station["gpsfix"] == 1) or (station["gpsfix"] == 2): #might not actually need this for telemetry!
            # Extract stations
            node = station["callsign"] + "-" + str(station["id"])
            destNode = station["destcallsign"] + "-" + str(station["destid"])

            if station["aprf"] == 1:
                labelString = node + '>GPSFDY,' + 'qAR,' + destNode + '::' + node + ' :' + "UNIT." + str(unit0[:6]) + ',' + str(unit1[:6]) + ',' + str(unit2[:5]) + ',' + str(unit3[:5]) + ',' + str(unit4[:4]) + ',' + str(bLabel0[:5]) + ',' + str(bLabel1[:4]) + ',' + str(bLabel2[:3]) + ',' + str(bLabel3[:3]) + ',' + str(bLabel4[:3]) + ',' + str(bLabel5[:2]) + ',' + str(bLabel6[:2]) + ',' + str(bLabel7[:2]) + '\r'
            else:
                labelString = node + '>GPSFDY' + '::' + node + ' :' + "UNIT." + str(unit0[:6]) + ',' + str(unit1[:6]) + ',' + str(unit3[:5]) + ',' + str(unit3[:5]) + ',' + str(unit4[:4]) + ',' + str(bLabel0[:5]) + ',' + str(bLabel1[:4]) + ',' + str(bLabel2[:3]) + ',' + str(bLabel3[:3]) + ',' + str(bLabel4[:3]) + ',' + str(bLabel5[:2]) + ',' + str(bLabel6[:2]) + ',' + str(bLabel7[:2]) + '\r'
            print labelString
            aprs = connectAPRSIS()
            aprs.sendall(labelString)
            aprs.close()

def aprsParameters(data):
    """Specifies the names of channels for APRS telemetry and sends them to APRS-IS"""
    #temporary
    ADC0 = "ADC0"
    ADC1 = "ADC1"
    ADC2 = "ADC2"
    ADC3 = "ADC7"
    ADC4 = "ADC8"
    IO0 = "IO"
    IO1 = "IO"
    IO2 = "IO"
    IO3 = "IO"
    IO4 = "IO"
    IO5 = "IO"
    IO6 = "IO"
    IO7 = "BT"

    for station in data:
        station = station[0]
        if (station["gpsfix"] == 1) or (station["gpsfix"] == 2): #might not actually need this for telemetry!
            # Extract stations
            node = station["callsign"] + "-" + str(station["id"])
            destNode = station["destcallsign"] + "-" + str(station["destid"])
            print node
            try:
                if station["aprf"] == 1:
                    paramString = node + '>GPSFDY,' + 'qAR,' + destNode + '::' + node + ' :' + "PARM." + str(ADC0[:6]) + ',' + str(ADC1[:6]) + ',' + str(ADC2[:5]) + ',' + str(ADC3[:5]) + ',' + str(ADC4[:4]) + ',' + str(IO0[:5]) + ',' + str(IO1[:4]) + ',' + str(IO2[:3]) + ',' + str(IO3[:3]) + ',' + str(IO4[:3]) + ',' + str(IO5[:2]) + ',' + str(IO6[:2]) + ',' + str(IO7[:2]) + '\r'
                else:
                    paramString = node + '>GPSFDY' + '::' + node + ' :' + "PARM." + str(ADC0[:6]) + ',' + str(ADC1[:6]) + ',' + str(ADC2[:5]) + ',' + str(ADC3[:5]) + ',' + str(ADC4[:4]) + ',' + str(IO0[:5]) + ',' + str(IO1[:4]) + ',' + str(IO2[:3]) + ',' + str(IO3[:3]) + ',' + str(IO4[:3]) + ',' + str(IO5[:2]) + ',' + str(IO6[:2]) + ',' + str(IO7[:2]) + '\r'
            except StandardError as e:
                print e
            print paramString

            aprs = connectAPRSIS()
            aprs.sendall(paramString)
            aprs.close()

def aprsEquations(data):
    """Specifies the scaling values for APRS telemetry and sends them to APRS-IS"""
    #temporary
    EQ0A = 0
    EQ0B = 1
    EQ0C = 0
    EQ1A = 0
    EQ1B = 1
    EQ1C = 0
    EQ2A = 0
    EQ2B = 1
    EQ2C = 0
    EQ3A = 0
    EQ3B = 1
    EQ3C = 0
    EQ4A = 0
    EQ4B = 1
    EQ4C = 0


    for station in data:
        station = station[0]
        if (station["gpsfix"] == 1) or (station["gpsfix"] == 2): #might not actually need this for telemetry!
            # Extract stations
            node = station["callsign"] + "-" + str(station["id"])
            destNode = station["destcallsign"] + "-" + str(station["destid"])

            if station["aprf"] == 1:
                equationString = node + '>GPSFDY,' + 'qAR' + destNode + '::' + node + ' :' + "EQNS." + str(EQ0A) + ',' + str(EQ0B) + ',' + str(EQ0C) + ',' + str(EQ1A) + ',' + str(EQ1B) + ',' + str(EQ1C) + ',' + str(EQ2A) + ',' + str(EQ2B) + ',' + str(EQ2C) + ',' + str(EQ3A) + ',' + str(EQ3B) + ',' + str(EQ3C) + ',' + str(EQ4A) + ',' + str(EQ4B) + ',' + str(EQ4C) + '\r'
            else:
                equationString = node + '>GPSFDY' + '::' + node + ' :' + "EQNS." + str(EQ0A) + ',' + str(EQ0B) + ',' + str(EQ0C) + ',' + str(EQ1A) + ',' + str(EQ1B) + ',' + str(EQ1C) + ',' + str(EQ2A) + ',' + str(EQ2B) + ',' + str(EQ2C) + ',' + str(EQ3A) + ',' + str(EQ3B) + ',' + str(EQ3C) + ',' + str(EQ4A) + ',' + str(EQ4B) + ',' + str(EQ4C) + '\r'
            print equationString
            aprs = connectAPRSIS()
            aprs.sendall(equationString)
            aprs.close()

def aprsMain():
	telemSequence = 0
	#aprs = connectAPRSIS()
	time.sleep(5) # Let localhost server start up
	while True:
		#aprs = connectAPRSIS()
		try:
			time.sleep(1)
			stations = getCurrentStations()
			data = getStationData(stations)
			aprsPosition(data)
			telemSequence = aprsTelemetry(telemSequence,data)
			aprsLabels(data)
			aprsParameters(data)
			aprsEquations(data)
		except StandardError as e:
			print e
		except IOError as e:
			if e.errno == errno.EPIPE:
				aprs.close()
				print e
				print "Broken pipe"

		if telemSequence > 999:
			mSequence = 0
		time.sleep(60)

def main():
    #uncomment aprsMain and comment out threading to debug seperatedly with proxy running in background
    #aprsMain()
    threads = []
    t1 = threading.Thread(target = aprsMain)
    threads.append(t1)
    t1.start()


if __name__ == '__main__':
    main()
