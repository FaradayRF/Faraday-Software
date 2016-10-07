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
import sys

filename = sys.argv[1]

#blinkLED_f6459.txt

f = open(filename, 'r')

mem_addr_index = []
section_data_index = []
file_program_hex = f.read()

def ParseTiTxtHexFile(input_file):
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
        mem_addr_index.append(mem_addr)
        section_data_index.append(section_data.decode('hex'))

def CalcTiTxtCrc16(databytes):
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

def CreateOutputFile():
    textfile = open("Program_CRC_Calculations.txt", 'w')
    for i in range(0, len(mem_addr_index)):
        final_addr = mem_addr_index[i].encode('hex')
        final_len = hex(len(section_data_index[i]))
        final_crc = hex(CalcTiTxtCrc16(section_data_index[i]))

        #Script Format
        script_index_crc = "CRC_CHECK "+"0x"+str(final_addr)+' '+str(final_len)+' '+str(final_crc)
        crc_script_index.append(str(script_index_crc))
        textfile.writelines(("Memory Address: 0x", final_addr,"\n"))
        textfile.writelines(("Data Length: ", final_len,"\n"))
        textfile.writelines(("CRC: ", final_crc))
        textfile.writelines(('\n', script_index_crc))
        textfile.writelines('\n\n')


def CreateBslScript():
    textfile = open("FaradayFirmwareUpgradeScript.txt", 'w')
    textfile.writelines(('MODE 6xx UART 9600 COM3 PARITY', '\n'))
    textfile.writelines(('CHANGE_BAUD_RATE 115200', '\n'))
    textfile.writelines(('VERBOSE', '\n'))
    textfile.writelines(('RX_PASSWORD pass32_wrong.txt', '\n')) #//gives the wrong password to mass erase the memory
    textfile.writelines(('RX_PASSWORD pass32_default.txt', '\n'))
    textfile.writelines(('RX_DATA_BLOCK ', filename, '\n'))
    for i in range(0, len(crc_script_index)):
        textfile.writelines((str(crc_script_index[i]), '\n'))





ParseTiTxtHexFile(file_program_hex)
CreateOutputFile()
CreateBslScript()

