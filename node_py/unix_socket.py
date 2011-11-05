try:
    from SocketServer import *
except ImportError:
    from socketserver import *

import json

import json_segment
import actions

class NoFSUnixServer(UnixStreamServer):
    pass

class NoFSUnixHandler(StreamRequestHandler):
    def handle(self):
        while True:
            data = json_segment.next_json(self.rfile)
            print("Received: {}".format(data))
            request = json.loads(data)
            result = actions.handle(request)
            if result == False:
                print("Disconnecting")
                return
            self.wfile.write(json.dumps(result))

def serve_unix():
    server = NoFSUnixServer("/tmp/nofs.socket", NoFSUnixHandler)
    print("Starting Unix sockets server")
    server.serve_forever()
