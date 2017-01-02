import aprs

aprs.main()

station1 = {}

station1["SOURCECALLSIGN"] = 'KB1LQD'
station1["SOURCEID"] = 5
station1["DESTINATIONCALLSIGN"] = 'KB1LQD'
station1["DESTINATIONID"] = 1
station1["GPSLATITUDE"] = 4233.6997
station1["GPSLONGITUDE"] = 07123.0185
station1["GPSLATITUDEDIR"] = 'N'
station1["GPSLONGITUDEDIR"] = 'W'
station1["GPSALTITUDE"] = 100
station1["GPSSPEED"] = 0
station1["GPSFIX"] = 2

aprs.sendPositions(station1, aprs.connectAPRSIS())


### Get APRS configuration
##qConstruct = aprsConfig.get('aprs', 'qconstruct')
##dataTypeIdent = aprsConfig.get('aprs', 'datatypeident')
##destAddress = aprsConfig.get('aprs', 'destaddress')
##symbolTable = aprsConfig.get('aprs', 'symboltable')
##symbol = aprsConfig.get('aprs', 'symbol')
##altSymbolTable = aprsConfig.get('aprs', 'altsymboltable')
##altSymbol = aprsConfig.get('aprs', 'altsymbol')
##comment = aprsConfig.get('aprs', 'comment')
##altComment = aprsConfig.get('aprs', 'altcomment')