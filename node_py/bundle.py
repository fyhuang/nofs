import os.path

import config

class Bundle(object):
    def __init__(self, name):
        self.path = os.path.join(config.root_dir, name)

    def valid(self):
        if os.path.isdir(self.path) and not os.path.islink(self.path):
            # TODO: is 'not islink' a good idea?
            return True
        return False

    def path_to_file(self, path):
        if len(path) == 0:
            return None
        if path == '/':
            return None
        if path[0] == '/':
            path = path[1:]
        return os.path.join(self.path, path)
