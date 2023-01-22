from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal


class ThreadTimer(QThread):
    signalTimeout = pyqtSignal(str)

    def __init__(self, callbackFunction, dataForCallbackFunction=None, toutMs=1000, repeats=1):
        QThread.__init__(self)
        self.callbackFunction = callbackFunction

        self.dataForCallbackFunction = dataForCallbackFunction

        self.timeoutMs = toutMs

        self.resendRepeats = repeats

        self.start()


    def run(self):
        for _ in range(self.resendRepeats):
            self.msleep(self.timeoutMs)
            self.callbackFunction(self.dataForCallbackFunction)

        self.msleep(10)
