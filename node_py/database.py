# Log-structured database? (MVCC)

class Database(object):
    def __init__(self, network, dbfilename):
        self._d = {}

    def sync(self):
        pass
