import threading

class SharedData(object):
    def __init__(self):
        self.running = True
        self.file_index = None

        self.state_lock = threading.Lock()
