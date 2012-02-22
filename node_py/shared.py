import threading

class SharedData(object):
    def __init__(self, node):
        self.running = True
        self.state_lock = threading.Lock()

        self.node = node
        self.peers = {}

        self.local = threading.local()
