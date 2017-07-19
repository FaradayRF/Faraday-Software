#-------------------------------------------------------------------------------
# Name:        /faraday/classes/faradayFTDI.py
# Purpose:     Control FTDI chip during Bootstrap Loader operation
#
# Author:      Brenton Salmi, Bryce Salmi
#
# Created:     07/19/2017
# Licence:     GPLv3
#-------------------------------------------------------------------------------

import ctypes
import ctypes.wintypes
import time

class FtdiD2xxCbusControlObject(object):
    """
    This class controls the FTDI FT230X during bootloading
    """

    def __init__(self):
        """
        initialize the class and variables
        """
        self.BITMASK_IO_OUTPUTS = 0xF0
        self.BITMASK_IO_OUTPUTS_RESET = 0x40
        self.BITMASK_IO_INPUTS = 0x00
        self.BITMASK_RST = 0x01
        self.BITMASK_TEST = 0x02
        self.DELAY_TIME = 1
        self.handle = ''
        self.ftd2xxDll = ''

    def ResetToggle(self):
        """
        Toggle reset IO

        :return: None
        """
        ##RESET LOW
        self.ftd2xxDll.FT_SetBitMode(self.handle, self.BITMASK_IO_OUTPUTS_RESET | self.BITMASK_RST, 0x20)
        ##Wait x
        time.sleep(10)

    def BslModeToggle(self):
        """
        Toggle CBUS to enter BSL mode

        :return: None
        """
        ##RESET LOW
        self.ftd2xxDll.FT_SetBitMode(self.handle, self.BITMASK_IO_OUTPUTS, 0x20)
        ##Wait x
        time.sleep(self.DELAY_TIME)
        ##TEST HIGH
        self.ftd2xxDll.FT_SetBitMode(self.handle, self.BITMASK_IO_OUTPUTS | self.BITMASK_TEST, 0x20)
        ##Wait x
        time.sleep(self.DELAY_TIME)
        ##TEST LOW
        self.ftd2xxDll.FT_SetBitMode(self.handle, self.BITMASK_IO_OUTPUTS, 0x20)
        ##Wait x
        time.sleep(self.DELAY_TIME)
        ##TEST HIGH
        self.ftd2xxDll.FT_SetBitMode(self.handle, self.BITMASK_IO_OUTPUTS | self.BITMASK_TEST, 0x20)
        ##Wait x
        time.sleep(self.DELAY_TIME)
        ##RESET HIGH
        self.ftd2xxDll.FT_SetBitMode(self.handle, self.BITMASK_IO_OUTPUTS | self.BITMASK_TEST | self.BITMASK_RST, 0x20)
        ##Wait x
        time.sleep(self.DELAY_TIME)
        ##TEST LOW
        self.ftd2xxDll.FT_SetBitMode(self.handle, self.BITMASK_IO_OUTPUTS | self.BITMASK_RST, 0x20)
        time.sleep(self.DELAY_TIME)

    def NominalModeToggle(self):
        """
        Toggle FTDI IC into nominal mode

        :return: None
        """
        self.ftd2xxDll.FT_SetBitMode(self.handle, self.BITMASK_IO_INPUTS, 0x20)

    def NominalForcedToggle(self):
        """
        Force FTDI IC into nominal mode

        :return: None
        """
        self.ftd2xxDll.FT_SetBitMode(self.handle, self.BITMASK_IO_OUTPUTS | self.BITMASK_RST, 0x20)

    def DisableBslToggle(self):
        """
        Disable FTDI IC Bootstrap loader toggling. Toggle CBUS to leave BSL mode per Errata (Reset won't work)

        :return: None
        """
        ##RESET HIGH TEST LOW
        self.ftd2xxDll.FT_SetBitMode(self.handle, self.BITMASK_IO_OUTPUTS | self.BITMASK_RST, 0x20)
        ##Wait x
        time.sleep(self.DELAY_TIME)
        ##RESET HIGH TEST HIGH
        self.ftd2xxDll.FT_SetBitMode(self.handle, self.BITMASK_IO_OUTPUTS | self.BITMASK_TEST | self.BITMASK_RST, 0x20)
        ##Wait x
        time.sleep(self.DELAY_TIME)
        ##RESET HIGH TEST LOW
        self.ftd2xxDll.FT_SetBitMode(self.handle, self.BITMASK_IO_OUTPUTS | self.BITMASK_RST, 0x20)
        ##Wait x
        time.sleep(self.DELAY_TIME)
        ##RESET HIGH TEST HIGH
        self.ftd2xxDll.FT_SetBitMode(self.handle, self.BITMASK_IO_OUTPUTS | self.BITMASK_TEST | self.BITMASK_RST, 0x20)
        ##Wait x
        time.sleep(self.DELAY_TIME)
        ##RESET HIGH TEST LOW
        self.ftd2xxDll.FT_SetBitMode(self.handle, self.BITMASK_IO_OUTPUTS | self.BITMASK_RST, 0x20)
        ##Wait x
        time.sleep(self.DELAY_TIME)
        ##RESET LOW TEST LOW
        self.ftd2xxDll.FT_SetBitMode(self.handle, self.BITMASK_IO_OUTPUTS, 0x20)
        ##Wait x
        time.sleep(self.DELAY_TIME)
        ##RESET HIGH TEST LOW
        self.ftd2xxDll.FT_SetBitMode(self.handle, self.BITMASK_IO_OUTPUTS | self.BITMASK_RST, 0x20)

    def Connect(self):
        """
        Use FTDI dll files to connect to IC

        :return: None
        """
        self.ftd2xxDll = ctypes.windll.LoadLibrary('ftd2xx.dll')
        self.handle = ctypes.wintypes.DWORD()
        assert self.ftd2xxDll.FT_Open(0, ctypes.byref(self.handle)) == 0

        assert self.ftd2xxDll.FT_SetTimeouts(self.handle, 1, 1) == 0
        assert self.ftd2xxDll.FT_SetBaudRate(self.handle, 38400) == 0
        assert self.ftd2xxDll.FT_SetDataCharacteristics(self.handle, ctypes.c_byte(8), ctypes.c_ubyte(0), ctypes. c_ubyte(0)) == 0
        assert self.ftd2xxDll.FT_SetFlowControl(self.handle, 0x0000, ctypes.c_byte(0), ctypes.c_byte(0)) == 0
        assert self.ftd2xxDll.FT_Purge(self.handle, 3) == 0

    def Disconnect(self):
        """
        Use FTDI dll files to disconnect from IC

        :return: None
        """
        self.ftd2xxDll.FT_Close(self.handle)
        try:
            ctypes.windll.kernel32.FreeLibrary(self.ftd2xxDll._handle)
        except:
            print "FAILED DISCONNECT"
        self.ftd2xxDll._handle = None
        return True

    def EnableBslMode(self):
        """
        Enable FTDI IC bootstrap loader mode

        :return: None
        """
        self.Connect()
        self.BslModeToggle()
        self.NominalModeToggle()
        self.Disconnect()
        return True

    def DisableBslMode(self):
        """
        Disable FTDI IC bootstrap loader mode

        :return: None
        """
        self.Connect()
        self.DisableBslToggle()
        self.NominalModeToggle()
        self.Disconnect()
        return True

    def PerformStandardReset(self):
        """
        Perform reset with FTDI IC

        :return: None
        """
        self.Connect()
        self.ResetToggle()
        self.NominalModeToggle()
        self.Disconnect()
        return True

    def SetResetHigh(self):
        """
        Set FTDI IC reset pin to high

        :return: None
        """
        ##RESET HIGH TEST LOW
        self.ftd2xxDll.FT_SetBitMode(self.handle, self.BITMASK_IO_OUTPUTS | self.BITMASK_RST, 0x20)
