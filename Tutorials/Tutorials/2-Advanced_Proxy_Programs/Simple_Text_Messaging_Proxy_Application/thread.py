import time
from threading import Thread
import threading

def myfunc(i):
    print 'Test %d' % i
    time.sleep(1)
    print 'Finished %d' % i

#t = Thread(target=myfunc, args=(1,))
#t.start()

