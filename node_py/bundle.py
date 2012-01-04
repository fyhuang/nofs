import os
import os.path
import stat
import time

import config
import packet

class Bundle(object):
    def __init__(self, name):
        self.path = os.path.join(config.root_dir, name)

    def valid(self):
        if os.path.isdir(self.path) and not os.path.islink(self.path):
            # TODO: is 'not islink' a good idea?
            return True
        return False

    def path_to(self, path):
        if len(path) == 0:
            return None
        if path == '/':
            return None
        if path[0] == '/':
            path = path[1:]
        return os.path.join(self.path, path)

    # TODO: should this belong in here?
    def stat(self, path):
        fullpath = self.path_to(path)
        if fullpath is None:
            print("Invalid path")
            return None

        try:
            stat_res = os.stat(fullpath)
        except OSError:
            print("Couldn't stat")
            return None

        ctime_loc = stat_res.st_ctime
        ctime_utc = int(time.mktime(time.gmtime(ctime_loc)))

        if stat.S_ISREG(stat_res.st_mode):
            ftype = b'f'
        elif stat.S_ISDIR(stat_res.st_mode):
            ftype = b'd'
        else:
            print("Isn't file or dir")
            return None

        return packet.StatResponse(ftype, ctime_utc, stat_res.st_size)
