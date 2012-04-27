import os
import sys
import os.path

import config
from local.unix_server import *
#from http_server import *
#from tcp_server import *
import shared
from peer_node import PeerNode

def main(argv=None):
    if sys.version_info[0] == 2 and sys.version_info[1] < 7:
        print("This program requires Python >2.7")
        sys.exit()
    if argv is None:
        argv = sys.argv

    # Check for data dir existence
    if not os.path.isdir(config.DATA_DIR):
        print("Data dir doesn't exist!")
        sys.exit()
    lists_dir = os.path.join(config.DATA_DIR, 'lists')
    if not os.path.isdir(lists_dir):
        print("Creating lists dir")
        os.mkdir(lists_dir)
    blocks_dir = os.path.join(config.DATA_DIR, 'blocks')
    if not os.path.isdir(blocks_dir):
        print("Creating blocks dir")
        os.mkdir(blocks_dir)

    # Initialize
    node = PeerNode("localhost", "localhost")
    shared.sd = shared.SharedData(node)

    # Start servers
    serve_unix_thread()
    #serve_http_thread("localhost", 16637, sd)
    #serve_tcp("localhost", 6637, sd)
    while True:
        import time
        time.sleep(1)

if __name__ == "__main__":
    main()
