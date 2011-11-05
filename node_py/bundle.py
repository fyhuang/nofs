import os.path

import config

class Bundle(object):
    def __init__(self, name):
        self.path = os.path.join(config.root_dir, name)

    def valid(self):
        if os.path.isdir(path) and not os.path.islink(path):
            # TODO: is 'not islink' a good idea?
            return True
        return False

    def path_to_file(self, path):
        return os.path.join(self.path, path)
