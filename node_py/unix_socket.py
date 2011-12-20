try:
    from SocketServer import *
except ImportError:
    from socketserver import *

import json
import os
import os.path
import inspect

import json_segment
import actions

class NoFSUnixServer(UnixStreamServer):
    pass

class NoFSUnixHandler(StreamRequestHandler):
    def handle(self):
        while True:
            data = json_segment.next_json(self.rfile)
            if data == None:
                print("Disconnecting (broken pipe)")
                return
            print("Received: {}".format(data))
            request = json.loads(data.decode())
            result = actions.handle(request)
            if result is None:
                print("Disconnecting (client request)")
                return

            if inspect.isgenerator(result):
                print("Sending multipart response")
                for p in result:
                    json.dump(p, self.wfile)
                    #self.wfile.write(json.dumps(p).encode())
            else:
                json.dump(result, self.wfile)
                #self.wfile.write(json.dumps(result).encode())

def serve_unix():
    SOCKET_FILE = "/tmp/nofs.socket"
    if os.path.exists(SOCKET_FILE):
        # TODO: check if server is already running
        os.remove(SOCKET_FILE)
    server = NoFSUnixServer(SOCKET_FILE, NoFSUnixHandler)
    print("Starting Unix sockets server")
    server.serve_forever()
