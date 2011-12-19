try:
    from SocketServer import *
except ImportError:
    from socketserver import *

import json
import os
import os.path

import json_segment
import actions

class NoFSUnixServer(UnixStreamServer):
    pass

class NoFSUnixHandler(StreamRequestHandler):
    def handle(self):
        while True:
            data = json_segment.next_json(self.rfile)
            print("Received: {}".format(data))
            request = json.loads(data.decode())
            result = actions.handle(request)
            if result == False:
                print("Disconnecting")
                return
            self.wfile.write(json.dumps(result).encode())

def serve_unix():
    SOCKET_FILE = "/tmp/nofs.socket"
    if os.path.exists(SOCKET_FILE):
        # TODO: check if server is already running
        os.remove(SOCKET_FILE)
    server = NoFSUnixServer(SOCKET_FILE, NoFSUnixHandler)
    print("Starting Unix sockets server")
    server.serve_forever()
