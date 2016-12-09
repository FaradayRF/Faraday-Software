import tx
import rx
import threading
import time

t = rx.receiver()
t.start()

while 1:
    time.sleep(0.5)
    qsize = t.GetQueueSize()
    print qsize
    if(qsize>3):
        while(t.GetQueueSize() > 0):
            print t.fifo.get_nowait()

