import threading

class SharedData(object):
    def __init__(self, node):
        self.stop_evt = threading.Event()

        self.node = node
        self.peers = {}

sd = None
