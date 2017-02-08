import os
import subprocess

#from BSL_Files import Faraday_BSL_FTDI_CBUS

class createFirmwareScript(object):
    def __init__(self, firmware_path):
        self.firmware_path = firmware_path
    def test(self):
        firmware_filename = 'Firmware\Faraday_D1_Release.txt'
        #os.system("Create_TI-TXT_Parse.py " + firmware_filename)