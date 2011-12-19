import sys

from unix_socket import *

def main(argv=None):
    if sys.version_info[0] < 3:
        print("This program requires Python 3")
        sys.exit()
    if argv is None:
        argv = sys.argv
    # Start servers
    serve_unix()

if __name__ == "__main__":
    main()
