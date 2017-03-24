import arq

listdata = ['this ', 'is', ' a', ' test', '.']

def transmitroutine( data):
    print "Transmitting: ", data

testtxsm = arq.TransmitArqStateMachine(listdata, transmitroutine)
testtxsm.newdataqueue(listdata)

testtxsm.runstate()

testtxsm.updatestate(arq.STATE_START)

testtxsm.runstate()
testtxsm.runstate()
testtxsm.runstate()
testtxsm.runstate()
testtxsm.ackreceived()
testtxsm.runstate()
testtxsm.runstate()
testtxsm.runstate()
testtxsm.runstate()
testtxsm.ackreceived()
testtxsm.runstate()
testtxsm.runstate()
testtxsm.runstate()
testtxsm.ackreceived()
testtxsm.runstate()
testtxsm.runstate()
testtxsm.runstate()
testtxsm.ackreceived()
testtxsm.runstate()
testtxsm.runstate()
testtxsm.runstate()
testtxsm.ackreceived()
testtxsm.runstate()
testtxsm.runstate()
testtxsm.runstate()