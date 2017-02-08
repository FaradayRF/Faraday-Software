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
import os
import subprocess

from BSL_Files import Faraday_BSL_FTDI_CBUS

#firmware_filename = sys.argv[1]
firmware_filename = 'Firmware\Faraday_D1_Release.txt'
os.system("BSL_Files\Create_TI-TXT_Parse.py " + firmware_filename)

##Enable BSL Mode
#device_bsl = Faraday_BSL_FTDI_CBUS.FtdiD2xxCbusControlObject()

#device_bsl.EnableBslMode()
#subprocess.call(['BSL_Files\bsl-scripter-windows.exe', 'BSL_Files\FaradayFirmwareUpgradeScript.txt'])
#device_bsl.DisableBslMode()