#-------------------------------------------------------------------------------
# Name:        /faraday/classes/createtiscript.py
# Purpose:     Texas Instruments bootloader script creation class
#
# Author:      Brenton Salmi, Bryce Salmi
#
# Created:     03/08/2016
# Licence:     GPLv3
#-------------------------------------------------------------------------------

import array
import os
import sys

class CreateTiBslScript(object):
    """
    This class creates a TI Bootstrap Loader script file from a text file of Faraday firmware
    """

    def __init__(self, path, filename, comport, outputfilename, upgradeScript, logger):
        """
        initialize the class and variables
        """

        self.path = path
        self._filename = os.path.join(os.path.expanduser('~'), '.faraday', 'firmware', filename)
        self.comport = comport
        self.mem_addr_index = []
        self.section_data_index = []
        self._outputfilename = outputfilename
        self._upgradeScript = upgradeScript
        self.logger = logger

    def createscript(self):
        """
        Create the TI Boostrap loader script

        :return: None
        """

        try:
            f = open(os.path.join(self.path,self._filename), 'r')
            file_program_hex = f.read()

        except:
            # File likely doesn't exist, warn user and exit
            self.logger.error('{0} doesn\'t exist!'.format(self._filename))
            self.logger.error('try --getmaster')
            sys.exit(1)

        self.ParseTiTxtHexFile(file_program_hex)
        self.CreateOutputFile(self._outputfilename)
        self.CreateBslScript(self._upgradeScript)


    def ParseTiTxtHexFile(self, input_file):
        """
        Parse the hex text file properly

        :param input_file: File object to parse
        :return: None
        """

        datasections = input_file.split('@')
        datasections.pop(0)  #remove empty first index

        # Remove memory addresses and separate data in each section
        for i in range(0, len(datasections)):
            # Parse and strip TI-TXT format
            a = datasections[i].replace('\n', '')
            a = a.replace(' ', '')
            mem_addr = str(a[0:4]).decode('hex')
            section_data = str(a[4:]).replace('q', '')  #remove end of file
            # Output
            self.mem_addr_index.append(mem_addr)
            self.section_data_index.append(section_data.decode('hex'))

    def CalcTiTxtCrc16(self, databytes):
        """
        Check text file CRC16 value

        :param databytes: data to perform CRC on
        :return: CRC value
        """

        data_array = array.array('B', databytes)
        chk = 0xffff
        for item in data_array:
            calc = 0
            calc = ((chk >> 8) ^ item) & 0xff
            calc ^= calc >> 4
            chk = (chk << 8) ^ (calc << 12) ^ (calc << 5) ^ calc
            chk = chk % 2**16
        return chk

    crc_script_index = []

    def CreateOutputFile(self, filename):
        """
        Create output TI bootstrap loader file from firmware text data

        :param filename: Bootstrap loader output data filename
        :return: CRC value
        """

        textfile = open(os.path.join(self.path,filename), 'w')
        for i in range(0, len(self.mem_addr_index)):
            final_addr = self.mem_addr_index[i].encode('hex')
            final_len = hex(len(self.section_data_index[i]))
            final_crc = hex(self.CalcTiTxtCrc16(self.section_data_index[i]))

            #Script Format
            script_index_crc = "CRC_CHECK 0x{} {} {}".format(
                str(final_addr), str(final_len), str(final_crc))
            self.crc_script_index.append(str(script_index_crc))
            textfile.writelines(("Memory Address: 0x", final_addr, "\n"))
            textfile.writelines(("Data Length: ", final_len, "\n"))
            textfile.writelines(("CRC: ", final_crc))
            textfile.writelines(('\n', script_index_crc))
            textfile.writelines('\n\n')

    def CreateBslScript(self, filename):
        """
        Create output TI bootstrap loader script from firmware text data

        :param filename: Bootstrap loader update script filename
        :return: CRC value
        """

        textfile = open(os.path.join(self.path,filename), 'w')
        textfile.writelines(("MODE 6xx UART 9600 ", str(self.comport), " PARITY", '\n'))
        textfile.writelines(("CHANGE_BAUD_RATE 115200", '\n'))
        textfile.writelines(("VERBOSE", '\n'))
        textfile.writelines(("RX_PASSWORD pass32_wrong.txt", '\n'))  #gives the wrong password to mass erase the memory
        textfile.writelines(("RX_PASSWORD pass32_default.txt", '\n'))
        textfile.writelines(("RX_DATA_BLOCK ", self._filename, '\n'))
        for i in range(0, len(self.crc_script_index)):
            textfile.writelines((str(self.crc_script_index[i]), '\n'))
