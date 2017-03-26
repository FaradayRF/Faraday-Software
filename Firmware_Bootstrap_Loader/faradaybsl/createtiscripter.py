#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Brent
#
# Created:     03/08/2016
# Copyright:   (c) Brent 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import array

#filename = sys.argv[1]
# filename = 'RF_Test_Firmware_1-17-17.txt'
# device_com_port = 32
#
# f = open(filename, 'r')
#
# mem_addr_index = []
# section_data_index = []
# file_program_hex = f.read()



#print "Arguement 0:", argument1


class CreateTiBslScript(object):

    def __init__(self, filename, comport):
        self.filename = filename
        self.comport = comport
        self.mem_addr_index = []
        self.section_data_index = []

    def createscript(self):
        f = open(self.filename, 'r')
        file_program_hex = f.read()
        self.ParseTiTxtHexFile(file_program_hex)
        self.CreateOutputFile()
        self.CreateBslScript()

    # ParseTiTxtHexFile(file_program_hex)
    # CreateOutputFile()
    # CreateBslScript()


    def ParseTiTxtHexFile(self, input_file):
        datasections = input_file.split('@')
        datasections.pop(0) #remove empty first index

        #remove memory addresses and separate data in each section
        for i in range(0, len(datasections)):
            #Parse and strip TI-TXT format
            a = datasections[i].replace('\n', '')
            a = a.replace(' ', '')
            mem_addr = str(a[0:4]).decode('hex')
            section_data = str(a[4:]).replace('q', '')#remove end of file
            #Ouput
            self.mem_addr_index.append(mem_addr)
            self.section_data_index.append(section_data.decode('hex'))

    def CalcTiTxtCrc16(self, databytes):
        data_array = array.array('B', databytes)
        chk = 0xffff
        for item in data_array:
            calc = 0
            calc = ((chk>>8)^item) & 0xff
            calc ^= calc>>4
            chk = (chk <<8)^(calc<<12)^(calc<<5)^calc
            chk = chk % 2**16
        return chk

    crc_script_index = []

    def CreateOutputFile(self):
        textfile = open("faradaybsl/Program_CRC_Calculations.txt", 'w')
        for i in range(0, len(self.mem_addr_index)):
            final_addr = self.mem_addr_index[i].encode('hex')
            final_len = hex(len(self.section_data_index[i]))
            final_crc = hex(self.CalcTiTxtCrc16(self.section_data_index[i]))

            #Script Format
            script_index_crc = "CRC_CHECK "+"0x"+str(final_addr)+' '+str(final_len)+' '+str(final_crc)
            self.crc_script_index.append(str(script_index_crc))
            textfile.writelines(("Memory Address: 0x", final_addr,"\n"))
            textfile.writelines(("Data Length: ", final_len,"\n"))
            textfile.writelines(("CRC: ", final_crc))
            textfile.writelines(('\n', script_index_crc))
            textfile.writelines('\n\n')


    def CreateBslScript(self):
        #global device_com_port
        #com_string = 'MODE 6xx UART 9600 COM%d PARITY' % device_com_port
        textfile = open("faradaybsl/FaradayFirmwareUpgradeScript.txt", 'w')
        textfile.writelines(("MODE 6xx UART 9600 ", str(self.comport), " PARITY", '\n'))
        textfile.writelines(("CHANGE_BAUD_RATE 115200", '\n'))
        textfile.writelines(("VERBOSE", '\n'))
        textfile.writelines(("RX_PASSWORD pass32_wrong.txt", '\n')) #//gives the wrong password to mass erase the memory
        textfile.writelines(("RX_PASSWORD pass32_default.txt", '\n'))
        print "Script file:", self.filename
        textfile.writelines(("RX_DATA_BLOCK ", "../", self.filename, '\n'))
        for i in range(0, len(self.crc_script_index)):
            textfile.writelines((str(self.crc_script_index[i]), '\n'))





#ParseTiTxtHexFile(file_program_hex)
#CreateOutputFile()
#CreateBslScript()

