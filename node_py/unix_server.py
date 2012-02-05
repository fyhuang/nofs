from socketserver import *

import os
import os.path

import proto
import local_proto

class NoFSUnixServer(UnixStreamServer):
    pass

class NoFSUnixHandler(StreamRequestHandler):
    def handle(self):
        client_proto = proto.determine(self.rfile)
        if client_proto not in ['local']:
            return

        while True:
            header = local_proto.Header.from_stream(self.rfile)
            print("Received: {}, {}".format(header.pkt_type, header.payload_len))
            pkt_data = self.rfile.read(header.payload_len)

            local_proto.handle(header, pkt_data, self.wfile)

def serve_unix():
    SOCKET_FILE = "/tmp/nofs.socket"
    if os.path.exists(SOCKET_FILE):
        # TODO: check if server is already running
        os.remove(SOCKET_FILE)
    server = NoFSUnixServer(SOCKET_FILE, NoFSUnixHandler)
    print("Starting Unix sockets server")
    server.serve_forever()
