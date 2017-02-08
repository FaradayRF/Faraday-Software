from BSL_Files import faradaybsl as faradaybsl

create_bsl = faradaybsl.createFirmwareScript('/Firmware/Faraday_D1_Release.txt')

print create_bsl.firmware_path