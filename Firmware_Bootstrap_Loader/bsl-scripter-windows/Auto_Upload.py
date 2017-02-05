#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Brent
#
# Created:     04/08/2016
# Copyright:   (c) Brent 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import sys
import subprocess
import os
import Faraday_BSL_FTDI_CBUS

#firmware_filename = sys.argv[1]
firmware_filename = 'RF_Test_Firmware_1-17-17.txt'
os.system("Create_TI-TXT_Parse.py " + firmware_filename)

#Enable BSL Mode
device_bsl = Faraday_BSL_FTDI_CBUS.FtdiD2xxCbusControlObject()

device_bsl.EnableBslMode()
subprocess.call(['bsl-scripter-windows.exe', 'FaradayFirmwareUpgradeScript.txt'])
device_bsl.DisableBslMode()