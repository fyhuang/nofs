import sys
import os.path

import config
from unix_server import *

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

    # Start servers
    serve_unix()

if __name__ == "__main__":
    main()
