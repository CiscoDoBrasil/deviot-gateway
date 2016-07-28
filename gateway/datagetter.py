__author__ = 'tingxxu'

import threading
import time


class DataGetter(threading.Thread):

    def __init__(self, manager):
        threading.Thread.__init__(self)
        self.manager = manager
        self.daemon = True

    def run(self):
        while True:
            self.manager.update(None)
            time.sleep(0.2)