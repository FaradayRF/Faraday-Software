import threading
import time


class TimerClass(threading.Thread):
    def __init__(self, funcptr, timeinterval):
        """
        This timer function is an abritrary threaded objects that executes the supplied function passed by
        reference on a periodic interval. The thread can also be stopped manually.

        :param funcptr: Pointer to the function to the run at every interval
        :param timeinterval: Interval (seconds) to run function
        """
        threading.Thread.__init__(self)
        self.event = threading.Event()
        self.funcptr = funcptr
        self.timeinterval = timeinterval

    def run(self):
        """
        The standard threaded class object run function that is run when .start() is called to the object.
        :return:
        """
        while not self.event.is_set():
            self.funcptr()
            self.event.wait(self.timeinterval)

    def stop(self):
        """
        Stop the timer
        :return:
        """
        self.event.set()