import sys
import os.path

import config
from unix_server import *
from http_server import *
from tcp_server import *
from shared import SharedData
from peer_node import PeerNode

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

    # Initialize
    node = PeerNode("localhost", "localhost")
    sd = SharedData(node)

    # Start servers
    #serve_unix_thread(sd)
    serve_http_thread("localhost", 16637, sd)
    #serve_tcp("localhost", 6637, sd)
    while True:
        import time
        time.sleep(1)

if __name__ == "__main__":
    main()
