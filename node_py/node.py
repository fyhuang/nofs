import sys

from unix_socket import *

def main(argv=None):
    if argv is None:
        argv = sys.argv
    # Start servers
    serve_unix()

if __name__ == "__main__":
    main()
