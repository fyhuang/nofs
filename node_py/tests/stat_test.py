import os
import os.path
import stat
import sys

import glob

attrs = [stat.ST_INO, stat.ST_DEV, stat.ST_NLINK, stat.ST_UID, stat.ST_GID, stat.ST_SIZE, stat.ST_ATIME, stat.ST_MTIME, stat.ST_CTIME]

for (dirpath, dirnames, filenames) in os.walk(sys.argv[1]):
    for f in filenames + dirnames:
        fn = os.path.join(dirpath, f)
        st = os.stat(fn)
        print(fn)
        print([st[a] for a in attrs])
