import ctypes, ctypes.wintypes
import time


class FtdiD2xxCbusControlObject(object):
    def __init__(self):
        self.BITMASK_IO_OUTPUTS = 0xF0
        self.BITMASK_IO_OUTPUTS_RESET = 0x40
        self.BITMASK_IO_INPUTS = 0x00
        self.BITMASK_RST = 0x01
        self.BITMASK_TEST = 0x02
        self.DELAY_TIME = 1
        self.handle = ''
        self.ftd2xxDll = ''

    def ResetToggle(self):
        #Currently Not working?
        ##RESET LOW
        self.ftd2xxDll.FT_SetBitMode(self.handle, self.BITMASK_IO_OUTPUTS_RESET | self.BITMASK_RST, 0x20)
        ##Wait x
        time.sleep(10)




    def BslModeToggle(self):
        #Toggle CBUS to enter BSL mode
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
        self.ftd2xxDll.FT_SetBitMode(self.handle, self.BITMASK_IO_INPUTS, 0x20)

    def NominalForcedToggle(self):
        self.ftd2xxDll.FT_SetBitMode(self.handle, self.BITMASK_IO_OUTPUTS | self.BITMASK_RST, 0x20)

    def DisableBslToggle(self):
        #Toggle CBUS to leave BSL mode per Errata (Reset won't work)
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
        self.ftd2xxDll = ctypes.windll.LoadLibrary('ftd2xx.dll')
        self.handle = ctypes.wintypes.DWORD()
        assert self.ftd2xxDll.FT_Open(0, ctypes.byref(self.handle)) == 0

        assert self.ftd2xxDll.FT_SetTimeouts(self.handle, 1, 1) == 0
        assert self.ftd2xxDll.FT_SetBaudRate(self.handle, 38400) == 0
        assert self.ftd2xxDll.FT_SetDataCharacteristics(self.handle, ctypes.c_byte(8), ctypes.c_ubyte(0), ctypes. c_ubyte(0)) == 0
        assert self.ftd2xxDll.FT_SetFlowControl(self.handle, 0x0000, ctypes.c_byte(0), ctypes.c_byte(0)) == 0
        assert self.ftd2xxDll.FT_Purge(self.handle, 3) == 0

    def Disconnect(self):
        self.ftd2xxDll.FT_Close(self.handle)
        try:
            ctypes.windll.kernel32.FreeLibrary(self.ftd2xxDll._handle)
        except:
            print "FAILED DISCONNECT"
        self.ftd2xxDll._handle = None
        return True

    def EnableBslMode(self):
        self.Connect()
        self.BslModeToggle()
        self.NominalModeToggle()
        self.Disconnect()
        return True

    def DisableBslMode(self):
        self.Connect()
        self.DisableBslToggle()
        self.NominalModeToggle()
        self.Disconnect()
        return True

    def PerformStandardReset(self):
        self.Connect()
        self.ResetToggle()
        self.NominalModeToggle()
        self.Disconnect()
        return True

        def SetResetHigh(self):
                ##RESET HIGH TEST LOW
                self.ftd2xxDll.FT_SetBitMode(self.handle, self.BITMASK_IO_OUTPUTS | self.BITMASK_RST, 0x20)






#Action
#BslMode()
#NominalMode()
#NominalForced()
#DisableBsl()

#writeBuffer = ctypes.create_string_buffer("abcdefghijklmnopqrstuvwxyz")
#bytesWritten = ctypes.wintypes.DWORD()
#assert self.ftd2xxDll.FT_Write(self.handle, writeBuffer, len(writeBuffer)-1, ctypes.byref(bytesWritten)) == 0
#print bytesWritten.value




