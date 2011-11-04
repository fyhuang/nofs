try:
    from SocketServer import *
except ImportError:
    from socketserver import *

import json_segment

class NoFSUnixServer(UnixStreamServer):
    pass

class NoFSUnixHandler(StreamRequestHandler):
    def __init__(self):
        pass
    def handle(self):
        data = json_segment.next_json(self.rfile)
        print("{} wrote: {}".format(self.client_address[0], data))

def serve_unix():
    server = NoFSUnixServer("/tmp/nofs.socket", NoFSUnixHandler)
    server.serve_forever()
