#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Brent
#
# Created:     07/08/2016
# Copyright:   (c) Brent 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sqlite3
import struct

## Deprecated script? Used?

#Open SQLite database, create one if not, timestamp ISO 8601 format
#timestamp = time.strftime("%Y-%m-%dT%H%M%S")
#db_filename = 'data/telemetry_' + timestamp + '.db'


#"SELECT * FROM Telemetry"



class HabPacketClass(object):
    def __init__(self, database_file, sqlschema_file):
        self.db_filename = database_file #'data/faraday.db'
        self.schema_filename = sqlschema_file #'telemetryschema.sql'
        self.conn = sqlite3.connect(self.db_filename)
        self.c= self.conn.cursor()
        self.count = 0
        self.keyidoffset = 0

    def GetBytestreamKeyids(self, keyidoffset):
        self.keyidoffset = keyidoffset
        try:
            self.c.execute("SELECT keyid, bytestream FROM telemetry WHERE bytestream IS NOT NULL and keyid >" + str(keyidoffset))
            keyid_index_list_temp = self.c.fetchall()
            keyid_index_dict = {}
            for i in range(0, len(keyid_index_list_temp)):
                keyid_index_dict[keyid_index_list_temp[i][0]] = keyid_index_list_temp[i][1]
            self.keyidoffset = max(keyid_index_dict)
            return keyid_index_dict
        except:
            return False

    def ParseSqlFileBytestream(self):
        self.c.execute("SELECT COUNT(bytestream) FROM telemetry")
        self.count = self.c.fetchone()[0]
        print "BYTESTREAM Count:", self.count
        self.c.execute("SELECT bytestream FROM telemetry")

    def SaveHabPacketToDatabase(self, packet):
        self.conn = sqlite3.connect(self.db_filename)
        self.c= self.conn.cursor()
        parsed_packet = self.ExtractHabPackets(packet)
        #self.c.execute("INSERT INTO HABApplication ('status_bitmask', 'uInt_timer_set', 'uInt_timer_remaining') VALUES(1,2,3)")
        self.c.execute("INSERT INTO HABApplication 'status_bitmask' VALUES(1)")
        print "SAVED"


    def ExtractHabPackets(self, str_packet):
         #HAB DATA TEMPORARY
        #print "HAB DATA", str(str_packet).encode('hex')
        header = '7E3C'.decode('hex')
        hab_packet_len = 7
        hab_list = []
        hab_packet_extracted = []
        i = str_packet.find(header)
        while i>= 0:
            hab_list.append(i)
            i = str_packet.find(header, i+1)
        #print "HAB LIST:", hab_list
        for item in hab_list:
            hab_pkt_sub = str_packet[item:(item+hab_packet_len)]
            hab_pkt = struct.unpack('>3B2H',hab_pkt_sub)
            #hab_packet_extracted.append(str_packet[item:(item+hab_packet_len)])
        return hab_pkt


def HabMainLoop(hab_object):
    newhabdata = hab_object.GetBytestreamKeyids(hab_object.keyidoffset)
    for item in newhabdata:
        extracted_packets = hab_object.ExtractHabPackets(newhabdata[item])
        hab_object.SaveHabPacketToDatabase(newhabdata[item])
        #INSERT INTO HABApplication ('uInt_timer_set', 'status_bitmask') VALUES(5, 6)
