try:
    from SocketServer import *
except ImportError:
    from socketserver import *

import os
import os.path
import inspect

import packet
import actions

class NoFSUnixServer(UnixStreamServer):
    pass

class NoFSUnixHandler(StreamRequestHandler):
    def handle(self):
        while True:
            header_data = self.rfile.read(packet.Header.binary_size)
            if len(header_data) == 0:
                print("Disconnecting (broken pipe)")
                return
            header = packet.Header.from_binary(header_data)
            print("Received: {}".format(header))
            result = actions.handle(header, self.rfile, self.wfile)
            if result == False: 
                print("Disconnecting (client request)")
                return

def serve_unix():
    SOCKET_FILE = "/tmp/nofs.socket"
    if os.path.exists(SOCKET_FILE):
        # TODO: check if server is already running
        os.remove(SOCKET_FILE)
    server = NoFSUnixServer(SOCKET_FILE, NoFSUnixHandler)
    print("Starting Unix sockets server")
    server.serve_forever()
