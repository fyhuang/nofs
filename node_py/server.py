import sys
import os.path

import config
from unix_server import *
from tcp_server import *
from shared import SharedData

def main(argv=None):
    if sys.version_info[0] < 3:
        print("This program requires Python 3")
        sys.exit()
    if argv is None:
        argv = sys.argv

    # Check for data dir existence
    if not os.path.isdir(config.DATA_DIR):
        print("Data dir doesn't exist!")
        sys.exit()

    sd = SharedData()

    # Start servers
    serve_unix()
    serve_tcp("localhost", 6637, sd)

if __name__ == "__main__":
    main()
