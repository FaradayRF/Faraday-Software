#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Bryce
#
# Created:     04/05/2016
# Copyright:   (c) Bryce 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import struct
import time
import sqlite3
from Command_Module import Command_Module
import base64
import requests
from ConfigParser import RawConfigParser
import parsing
import json
import CC430_Radio_Config


class faraday:
    """Describes a Faraday Modem's most basic identifiers"""

    def __init__ (self):
        self.latitude = [0, 0.0, 'N']
        self.longitude = [0, 0.0, 'W']
        self.altitude = [0,'M']
        self.speed = 0
        self.gpsfix = 0
        self.callsign = ''
        self.nodeid = 0
        self.hdop = 0.0

    def unpackTelemetry(self, data, b64=0):
        #Decode Base64 from JSON to raw byte packet
        if b64:
            data['data']  = base64.b64decode(data['data'])
        #Extract just the raw packet from JSON element
        tlm_raw = data['data']

        #Unpack the packet into Telemetry datagram
        tlm_no_checksum = struct.unpack('>121s 2x', data['data'])
        tlm = struct.unpack('>3B 118s 1H', data['data'])
        telem_datagram_pkt_type = tlm[0]
        telem_datagram_aprf = tlm[1]
        telem_datagram_payload_len = tlm[2]
        telem_datagram_payload = tlm[3]
        telem_datagram_error_detection_16 = tlm[4]

        #Compute checksum data
        comp_chk = parsing.compute_checksum_16(tlm_no_checksum[0], len(tlm_no_checksum[0]))

        # Should probable change checks of tlm[0] to telem_datagram_pkt_type
        #If packet type == 3 then unpacket packet type #3
        if( tlm[0] == 3):
            try:
                unpacket_telem_pkt_3 = self.telem_pkt_3_unpack(telem_datagram_payload)
                #print telem_datagram_pkt_type
                if(comp_chk == telem_datagram_error_detection_16):
                    chk_stat = True
                    return [telem_datagram_aprf, telem_datagram_pkt_type, unpacket_telem_pkt_3[0], unpacket_telem_pkt_3[1], comp_chk, telem_datagram_error_detection_16, chk_stat]
                else:
                    chk_stat = False
                    return [telem_datagram_aprf, telem_datagram_pkt_type, unpacket_telem_pkt_3[0], unpacket_telem_pkt_3[1], comp_chk, telem_datagram_error_detection_16, chk_stat]
            except IndexError as e:
                print "IndexError packet #3: ", e

        #If packet type == 2 then unpacket packet type #2
        elif( tlm[0] == 2):
            try:
                print"GOT TELEM 2"#, repr(telem_datagram_payload) #Length 118?
                unpacket_telem_pkt_2 = self.telem_pkt_2_unpack(telem_datagram_payload,0)
                print "\nPKT 2 Is:", repr(unpacket_telem_pkt_2)
                #print telem_datagram_pkt_type
                if(comp_chk == telem_datagram_error_detection_16):
                    chk_stat = True
                    return [telem_datagram_aprf, telem_datagram_pkt_type, unpacket_telem_pkt_2, comp_chk, telem_datagram_error_detection_16,chk_stat]
                else:
                    chk_stat = False
                    return [telem_datagram_aprf, telem_datagram_pkt_type, unpacket_telem_pkt_2, comp_chk, telem_datagram_error_detection_16,chk_stat]

            except IndexError as e:
                print "IndexError packet #2: ", e

        #If packet type == 1 then unpacket packet type #1
        elif( tlm[0] == 1):
            print "Get Telem Packet #1"
            unpacket_telem_pkt_1 = self.telem_pkt_1_unpack(telem_datagram_payload, 0)
            #print "\nPKT 1 Is: ", repr(telem_datagram_payload)
            #print comp_chk,telem_datagram_error_detection_16
            #if(comp_chk == telem_datagram_error_detection_16):
            if(True): #no checksum for this packet
                #print unpacket_telem_pkt_1
                chk_stat = True
                return [telem_datagram_aprf, telem_datagram_pkt_type, unpacket_telem_pkt_1, comp_chk, telem_datagram_error_detection_16]
            else:
                    return None #will probably error, need to change this. Rather it be atomic
        else:
            pass

    def telem_pkt_1_unpack(self, packet, debug):
        #Unpack telem datagram payload and extract telem packet 2
        telem_pkt_1 = struct.unpack('4s 114x', packet) #Parse out padding
        telem_pkt_1 = telem_pkt_1[0]

        #Parse telemetry packet type 2
        telem_pkt_1_parsed = struct.unpack('4B', telem_pkt_1)
        #print "Parsed", telem_pkt_2_parsed

        #Calculation device information
        cc430_rf_frequency_float = CC430_Radio_Config.freq0_reverse_carrier_calculation(26,telem_pkt_1_parsed[0], telem_pkt_1_parsed[1], telem_pkt_1_parsed[2], 0)
        cc430_rf_frequency_float = '%.3f'%cc430_rf_frequency_float #Truncate float to 3 decimal points

        if(debug==1):
            #Print information
            print "\n\n--Device Setting Information Telemetry (Packet #1)--"
            print "Unit Frequency:", cc430_rf_frequency_float, "MHz"
            print "Unit Power Level (PA Table):", telem_pkt_1_parsed[3], "(MAX=152)"
            print "\n\n"
        else:
            pass

        return telem_pkt_1_parsed

    def telem_pkt_2_unpack(self, packet, debug):
        #Unpack telem datagram payload and extract telem packet 2
        telem_pkt_2 = struct.unpack('14s 104x', packet) #Parse out padding
        telem_pkt_2 = telem_pkt_2[0]
        #print repr(telem_pkt_2)

        #Parse telemetry packet type 2
        telem_pkt_2_parsed = struct.unpack('<1H 12B', telem_pkt_2)

        if(debug==1):
            #Print information
            print "\n--DEVICE DEGUB FLASH INFO--"
            print "Boot Count:", telem_pkt_2_parsed[0]
            print "Reset Count:", telem_pkt_2_parsed[1]
            print "SYSRSTIV - BOR:", telem_pkt_2_parsed[2]
            print "SYSRSTIV - RST/NMI:", telem_pkt_2_parsed[3]
            print "SYSRSTIV - SVSL:", telem_pkt_2_parsed[4]
            print "SYSRSTIV - SVSH:", telem_pkt_2_parsed[5]
            print "SYSRSTIV - SVML_OVP:", telem_pkt_2_parsed[6]
            print "SYSRSTIV - SVMH_OVP:", telem_pkt_2_parsed[7]
            print "SYSRSTIV - WDT Time out:", telem_pkt_2_parsed[8]
            print "SYSRSTIV - Flash Key violation:", telem_pkt_2_parsed[9]
            print "SYSRSTIV - FLL unlock:", telem_pkt_2_parsed[10]
            print "SYSRSTIV - peripheral/config area fetch:", telem_pkt_2_parsed[11]
            print "SYSUNIV_ACCVIFG - Access Violation:", telem_pkt_2_parsed[12]
            print "\n"
        else:
            pass

        return telem_pkt_2_parsed

    def telem_pkt_3_unpack(self, packet):
        #print "Packet:", repr(packet)
        telemetry0 = struct.unpack('>9s 2B 9s 8B 1H 9s 1B 10s 1B 8s 1B 5s 1c 4s 3B 18s 2B 2H 21s', packet)
        byte_stream = telemetry0[26]
        telemetry1 = struct.unpack('>1H1H1H1H1H1H1H1h1H',telemetry0[25])

##        #HAB DATA TEMPORARY
##        print "HAB DATA", str(byte_stream).encode('hex')
##        header = '7E3C'.decode('hex')
##        hab_packet_len = 7
##        hab_list = []
##        i = byte_stream.find(header)
##        while i>= 0:
##            hab_list.append(i)
##            i = byte_stream.find(header, i+1)
##        print "HAB LIST:", hab_list
##        for item in hab_list:
##            hab_pkt_sub = byte_stream[item:(item+hab_packet_len)]
##            #hab_pkt_sub = hab_pkt_sub.decode('hex')
##            hab_pkt = struct.unpack('>3B2H',hab_pkt_sub)
##            print "\nHAB PACKET PARSED"
##            print str(byte_stream[item:(item+hab_packet_len)]).encode('hex')
##            print "STATUS BITMASK:", format(hab_pkt[2], '#010b')
##            print "TIMER SET:", hab_pkt[3]
##            print "TIMER CURRENT:", hab_pkt[4]
##            print "\n"
##        byte_stream.find(header)

        #Return function
        return [telemetry0, telemetry1]


    def parseTelemetry(self,port,aprf,pktType,telemetry0,telemetry1,accesspoint):
        try:
            callsign = telemetry0[0][:telemetry0[1]].encode('utf-8').strip()
            id = int(telemetry0[2])
        except StandardError as e:
            #can't print callsign if this errors soo...
            print "parseTelemetry: ", e

        try:
            destcallsign = telemetry0[3][:telemetry0[4]].encode('utf-8').strip()
            destid = int(telemetry0[5])

        except StandardError as e:
            print callsign,"-",id
            print "parseTelemetry: ", e

        try:
            altitude = float(telemetry0[17])
        except ValueError as e:
            print callsign,"-",id
            print "parseTelemetry: ", e
            altitude = None

        try:
            speed = float(telemetry0[19])
        except ValueError as e:
            print callsign,"-",id
            print "parseTelemetry: ", e
            speed = None

        try:
            latdec = float(telemetry0[13][2:])
        except ValueError as e:
            print callsign,"-",id
            print "parseTelemetry: ", e
            latdec = None

        try:
            londec = float(telemetry0[15][3:])
        except ValueError as e:
            print callsign,"-",id
            print "parseTelemetry: ", e
            londec = None

        try:
            hdop = float(telemetry0[21])
        except ValueError as e:
            print callsign,"-",id
            print "parseTelemetry: ", e
            hdop = None

        try:
            #maybe should check for correct value range here?
            latdeg = int(telemetry0[13][:2])
            latdir = chr(telemetry0[14])
            londeg = int(telemetry0[15][:3])
            londir = chr(telemetry0[16])
            altunits = chr(telemetry0[18])
            gpsfix = int(telemetry0[20])
            crc = 0 #int(telemetry0[26]) #Making 0 because I no longer pass this info to this function easily (BSALMI 6/22/16)

            if (gpsfix == 0):
                latdec = None;
                latdeg = None;
                latdir = None;
                londec = None;
                londeg = None;
                londir = None;
                altitude = None;
                altunits = None;
                speed = None;

            if (aprf == 0):
                accesspoint.callsign = callsign
                accesspoint.latitude = [latdeg,latdec,latdir]
                accesspoint.longitude = [londeg,londec,londir]
                accesspoint.altitude = [altitude,altunits]
                accesspoint.speed = speed
                accesspoint.hdop = hdop
                accesspoint.nodeid = id
                accesspoint.gpsfix = gpsfix


        except ValueError as e:
            print "parseTelemetry: ", e
        except IndexError as e:
            print "IndexError:", e, "\r"

        else:
            try:
                jsonTelemetry = {"faradayport":port,
                        "packettype": pktType,
                        "aprf":aprf,
                        "apcallsign": accesspoint.callsign,
                        "apid": accesspoint.nodeid,
                        "callsign": callsign,
                        "id": id,
                        "destcallsign": destcallsign,
                        "destid": destid,
                        "rtcsec":telemetry0[6],
                        "rtcmin":telemetry0[7],
                        "rtchour":telemetry0[8],
                        "rtcday":telemetry0[9],
                        "rtcdow":telemetry0[10],
                        "rtcmon":telemetry0[11],
                        "rtcyear":telemetry0[12],
                        "apgpsfix": accesspoint.gpsfix,
                        "aplatdeg": accesspoint.latitude[0],
                        "aplatdec": accesspoint.latitude[1],
                        "aplatdir": accesspoint.latitude[2],
                        "aplondeg": accesspoint.longitude[0],
                        "aplondec": accesspoint.longitude[1],
                        "aplondir":accesspoint.longitude[2],
                        "apaltitude":accesspoint.altitude[0],
                        "apaltunits": accesspoint.altitude[1],
                        "apspeed":accesspoint.speed,
                        "aphdop":accesspoint.hdop,
                        "gpsfix": gpsfix,
                        "latdeg": latdeg,
                        "latdec": latdec,
                        "latdir":latdir,
                        "londeg": londeg,# AP sending it's own data
                        "londec": londec,
                        "londir":londir,
                        "altitude":altitude, # AP sending it's own data
                        "altunits":altunits,
                        "speed":speed,
                        "hdop":hdop,
                        "gpio0":telemetry0[22],
                        "gpio1":telemetry0[23],
                        "gpio2":telemetry0[24],
                        "adc0":telemetry1[0],
                        "adc1":telemetry1[1],
                        "adc2":telemetry1[2],
                        "adc3":telemetry1[3],
                        "adc4":telemetry1[4],
                        "adc5":telemetry1[5],
                        "adc6":telemetry1[6],
                        "adc7":telemetry1[7],
                        "adc8":telemetry1[8],
                        "crc": crc,
                        "apepoch": time.time(),
                        "uChar_auto_cutdown_timer_state_status": telemetry0[26],
                        "uChar_cutdown_event_state_status": telemetry0[27],
                        "uInt_timer_set": telemetry0[28],
                        "uInt_timer_current": telemetry0[29]
                    }
                #print jsonTelemetry
                return jsonTelemetry
            except ValueError as e:
                print "parseTelemetry: ", e
                pass

    def parseDebugTelemetry(self,port,aprf,pktType,debugTelemetry):
        #print pktType,repr(debugTelemetry)
        try:
            bootCount = debugTelemetry[0]
            resetCount = debugTelemetry[1]
            bor = debugTelemetry[2]
            rstNMI = debugTelemetry[3]
            svsl = debugTelemetry[4]
            svsh = debugTelemetry[5]
            svmlOVP = debugTelemetry[6]
            svmhOVP = debugTelemetry[7]
            wdtto = debugTelemetry[8]
            flashKeyViolation = debugTelemetry[9]
            fllUnlock = debugTelemetry[10]
            peripheralConfigCnt = debugTelemetry[11]
            accessViolation = debugTelemetry[12]

        except StandardError as e:
            print "StandardError parsedDebugTelemetry: ", e
        except IndexError as e:
            print "IndexError parsedDebugTelemetry: ",
        else:
            try:
                jsonTelemetry = {"faradayport":port,
                        "packettype": pktType,
                        "epoch": time.time(),
                        "aprf":aprf,
                        "bootcount": bootCount,
                        "resetcount": resetCount,
                        "bor": bor,
                        "rstnmi": rstNMI,
                        "svsl": svsl,
                        "svsh": svsh,
                        "svmlovp": svmlOVP,
                        "svmhovp": svmhOVP,
                        "wdtto": wdtto,
                        "flashkeyviolation": flashKeyViolation,
                        "fllunlock": fllUnlock,
                        "peripheralconfigcnt": peripheralConfigCnt,
                        "accessviolation": accessViolation
                    }
                return jsonTelemetry

            except ValueError as e:
                print "parseDebugTelemetry: ", e


    def parseSystemSettings(self,port,aprf,pktType,systemSettings):
        try:
            rfFreq2 = systemSettings[0]
            rfFreq1 = systemSettings[1]
            rfFreq0 = systemSettings[2]
            rfPWR = systemSettings[3]

        except StandardError as e:
            print "StandardError parseSystemSettings: ", e
        except IndexError as e:
            print "IndexError parseSystemSettings: ",
        else:
            try:
                jsonTelemetry = {"faradayport":port,
                        "packettype": pktType,
                        "epoch": time.time(),
                        "aprf":aprf,
                        "rffreq2": rfFreq2,
                        "rffreq1": rfFreq1,
                        "rffreq0": rfFreq0,
                        "rfpwr": rfPWR
                }
                return jsonTelemetry

            except ValueError as e:
                print "parseDebugTelemetry: ", e

    def getScalingValues(self,callsign,nodeid):
        #print callsign,nodeid
        #Load from configuration file
        parser = RawConfigParser()
        parser.read('faraday.ini')
        port = parser.get('proxy','port')
        try:
            parameters = {'callsign':callsign, 'nodeid': nodeid}
            scalingRaw = requests.get("http://127.0.0.1:" + port + "/faraday/scaling", params=parameters)
            jsonScales = json.loads(scalingRaw.text)
            return jsonScales[0]

        except StandardError as e:
            print e

    def scaleTelemetry (self,jsonData,jsonScales, conn):
        #print jsonData
        #print jsonScales
        adc0 = jsonData['adc0'] * jsonScales['adc0m'] + jsonScales['adc0b']
        adc1 = jsonData['adc1'] * jsonScales['adc1m'] + jsonScales['adc1b']
        adc2 = jsonData['adc2'] * jsonScales['adc2m'] + jsonScales['adc2b']
        adc3 = jsonData['adc3'] * jsonScales['adc3m'] + jsonScales['adc3b']
        adc4 = jsonData['adc4'] * jsonScales['adc4m'] + jsonScales['adc4b']
        adc5 = jsonData['adc5'] * jsonScales['adc5m'] + jsonScales['adc5b']
        adc6 = jsonData['adc6'] * jsonScales['adc6m'] + jsonScales['adc6b']
        adc7 = jsonData['adc7']
        adc8 = jsonData['adc8'] * jsonScales['adc8m'] + jsonScales['adc8b']
        #print adc0, adc1, adc2, adc3, adc4, adc5, adc6, adc7, adc8

        #breakout GPIO values into a string array of binary values
        gpio0 = bin(jsonData['gpio0'])[2:].zfill(8) # pretty sure I flip these so watch for endianess
        gpio1 = bin(jsonData['gpio1'])[2:].zfill(8) # pretty sure I flip these so watch for endianess
        gpio2 = bin(jsonData['gpio2'])[2:].zfill(8) # pretty sure I flip these so watch for endianess
        #print gpio0
        #print gpio1
        #print gpio1[3], gpio1[4]



        c = conn.cursor()
        #Save data to local SQLite database
        try:
            # We should put these ordering/mappings into a config file...
            c.execute("INSERT INTO scaledtelemetry\
            (`adc0scaled`, `adc1scaled`, `adc2scaled`, `adc3scaled`,\
             `adc4scaled`, `adc5scaled`, `adc6scaled`, `adc7scaled`,\
             `adc8scaled`, `callsign`, `id`, `epoch`, `paenable`,\
             `lnaenable`,`hgmselect`, `mosfet`, `led1`, `led2`,`gpsreset`,\
             `gpsstandby`,`button`,`gpio0`,`gpio1`,`gpio2`,`gpio3`,`gpio4`,`gpio5`,`gpio6`,`gpio7`,`gpio8`,`gpio9`) \
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"\
            ,(adc0, adc1, adc2, adc3, adc4, adc5,\
            adc6, adc7, adc8, jsonData['callsign'], jsonData['id'],\
            jsonData['apepoch'], gpio2[0], gpio2[1], gpio2[2], gpio1[2],\
            gpio1[3],gpio1[4],gpio1[5],gpio1[6],gpio1[7],\
            gpio0[0],gpio0[1],gpio0[2],gpio0[3],gpio0[4],gpio0[5],gpio0[6],\
            gpio0[7],gpio1[0],gpio1[1]))

        except StandardError as e:
            print e

    def saveSQLTelem(self,jsonTelem,conn):
        c = conn.cursor()
        #Save data to local SQLite database
        try:
            c.execute("INSERT INTO telemetry\
            (`faradayport`,`packettype`,`aprf`,`apcallsign`,`apid`,`callsign`,\
            `id`,`rtcsec`,`rtcmin`,`rtchour`,`rtcday`,`rtcdow`,\
            `rtcmon`,`rtcyear`,'apgpsfix', `aplatdeg`,`aplatdec`,\
            `aplatdir`,`aplondeg`,`aplondec`,`aplondir`,\
            `apaltitude`,`apaltunits`,`apspeed`,`aphdop`,\
            'gpsfix', `latdeg`,`latdec`,`latdir`,\
            `londeg`,`londec`,`londir`,`altitude`,\
            `altunits`,`speed`,`hdop`,\
            `gpio0`,`gpio1`,`gpio2`,`adc0`,`adc1`,`adc2`,\
            `adc3`,`adc4`,`adc5`,`adc6`,`adc7`,`adc8`,\
            `apepoch`,`destcallsign`,`destid`,`crc`,'uChar_auto_cutdown_timer_state_status', 'uChar_cutdown_event_state_status', 'uInt_timer_set', 'uInt_timer_current')\
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,\
            ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,\
            ?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (jsonTelem['faradayport'],jsonTelem['packettype'],jsonTelem['aprf'],
            jsonTelem['apcallsign'],
            jsonTelem['apid'],jsonTelem['callsign'],
            jsonTelem['id'],jsonTelem['rtcsec'],
            jsonTelem['rtcmin'],jsonTelem['rtchour'],
            jsonTelem['rtcday'],jsonTelem['rtcdow'],
            jsonTelem['rtcmon'],jsonTelem['rtcyear'],jsonTelem['apgpsfix'],
            jsonTelem['aplatdeg'],jsonTelem['aplatdec'],
            jsonTelem['aplatdir'],jsonTelem['aplondeg'],
            jsonTelem['aplondec'],jsonTelem['aplondir'],
            jsonTelem['apaltitude'],
            jsonTelem['apaltunits'],
            jsonTelem['apspeed'],jsonTelem['aphdop'],
            jsonTelem['gpsfix'],
            jsonTelem['latdeg'],jsonTelem['latdec'],
            jsonTelem['latdir'],jsonTelem['londeg'],
            jsonTelem['londec'],jsonTelem['londir'],
            jsonTelem['altitude'],jsonTelem['altunits'],
            jsonTelem['speed'],jsonTelem['hdop'],
            jsonTelem['gpio0'],
            jsonTelem['gpio1'],jsonTelem['gpio2'],
            jsonTelem['adc0'],jsonTelem['adc1'],
            jsonTelem['adc2'],jsonTelem['adc3'],
            jsonTelem['adc4'],jsonTelem['adc5'],
            jsonTelem['adc6'],jsonTelem['adc7'],
            jsonTelem['adc8'],jsonTelem['apepoch'],
            jsonTelem['destcallsign'],jsonTelem['destid'],
            jsonTelem['crc'],
            jsonTelem['uChar_auto_cutdown_timer_state_status'],
            jsonTelem['uChar_cutdown_event_state_status'],
            jsonTelem['uInt_timer_set'],
            jsonTelem['uInt_timer_current'],
            ))


            #Commit SQL query
            conn.commit()

        except ValueError as e:
            print e
        except TypeError as e:
            print e
        except IndexError as e:
            print e
        except KeyError as e:
            print e

        #obtain telemetry scaling values and save scaled telemetry to database
        jsonScales = self.getScalingValues(jsonTelem['callsign'],jsonTelem['id'])
        self.scaleTelemetry(jsonTelem,jsonScales, conn)

    def saveSQLDebugTelem(self,jsonTelem,conn):
        c = conn.cursor()
        #Save data to local SQLite database
        try:
            #not saving callsign or node id yet
            c.execute("INSERT INTO faradayDebug\
            (`faradayport`,`packettype`,`aprf`,`epoch`,`bootcount`,`resetcount`,\
            `bor`,`rstnmi`,`svsl`,`svsh`,`svmlovp`,`svmhovp`,`wdtto`,`flashkeyviolation`,\
            `fllunlock`,`peripheralconfigcnt`,`accessviolation`)\
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (jsonTelem['faradayport'],jsonTelem['packettype'],jsonTelem['aprf'],
            jsonTelem['epoch'],jsonTelem['bootcount'],jsonTelem['resetcount'],
            jsonTelem['bor'],jsonTelem['rstnmi'],jsonTelem['svsl'],jsonTelem['svsh'],
            jsonTelem['svmlovp'],jsonTelem['svmhovp'],jsonTelem['wdtto'],
            jsonTelem['flashkeyviolation'], jsonTelem['fllunlock'],jsonTelem['peripheralconfigcnt'],
            jsonTelem['accessviolation']))


            #Commit SQL query
            conn.commit()

        except ValueError as e:
            print e
        except TypeError as e:
            print e
        except IndexError as e:
            print e
        except KeyError as e:
            print e

    def saveSQLSystemSettings(self,jsonTelem,conn):
        c = conn.cursor()
        #Save data to local SQLite database
        try:
            #not saving callsign or node id yet
            c.execute("INSERT INTO faradaySystemSettings\
            (`faradayport`,`packettype`,`aprf`,`epoch`,`rffreq0`,`rffreq1`,\
            `rffreq2`,`rfpwr`)\
            VALUES (?,?,?,?,?,?,?,?)",
            (jsonTelem['faradayport'],jsonTelem['packettype'],jsonTelem['aprf'],
            jsonTelem['epoch'],jsonTelem['rffreq0'],jsonTelem['rffreq1'],
            jsonTelem['rffreq2'],jsonTelem['rfpwr']))


            #Commit SQL query
            conn.commit()

        except ValueError as e:
            print "ValueError: ", e
        except TypeError as e:
            print "TypeError: ", e
        except IndexError as e:
            print "IndexError: ", e
        except KeyError as e:
            print "KeyError: ", e



    def create_config_packet(self):
        #Load from configuration file
        parser = RawConfigParser()
        parser.read('faraday.ini')

        #Create a device configuration class (this allows rolling creation/edit of the configuration packet)
        deviceConfig = Command_Module.Device_Config_Class()

        #Update bitmask for basic configurations
        config_bitmask = deviceConfig.update_bitmask_configuration(True)
        RFGPS_bitmask = deviceConfig.update_bitmask_gpio_p3(0,0,0,0,1,0,0,0)
        GPIO_bitmask = deviceConfig.update_bitmask_gpio_p4(0,0,0,1,0,0,0,0)
        #need update for IO config
        callsign = str(parser.get('faraday', 'callsign'))
        nodeid = int(parser.get('faraday','nodeid'))
        bootfreq = float(parser.get('faraday','bootfreq'))
        powerconf = int(parser.get('faraday','powerconf'))
        uarttelemboot = bool(parser.get('faraday','uarttelemboot'))
        rftelemboot= bool(parser.get('faraday','rftelemboot'))
        gpsboot = bool(parser.get('faraday','gpsboot'))
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
        RFGPS_bitmask, GPIO_bitmask)

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
        command_packet = Command_Module.create_command_packet(commandnum, packet_config)

        return command_packet

    def test_update(self):
        #Create test configuration packet
        config_packet_payload = self.create_config_packet()

        #Transmit configuration packet (Port 2)
        #service_number = 2
        #Faraday_Device.uartDevice.transmit_service_payload(int(service_number), len(config_packet_payload), config_packet_payload)

        b64cmd = base64.b64encode(config_packet_payload)
        #print b64cmd
        #status = requests.post('http://127.0.0.1:5000/faraday/2?cmd=%s' % b64cmd)
        status = requests.post('http://127.0.0.1/faraday/2?cmd=%s' % b64cmd)
        return status

def main():
    pass

if __name__ == '__main__':
    main()
