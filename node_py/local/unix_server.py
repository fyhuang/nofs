from SocketServer import *

import os
import os.path
import threading

import proto
from local import local_proto

class NoFSUnixServer(UnixStreamServer):
    pass

class NoFSUnixHandler(StreamRequestHandler):
    def handle(self):
        client_proto = proto.determine(self.rfile)
        if client_proto not in ['local']:
            print("Invalid protocol")
            return

        while True:
            header = local_proto.Header.from_stream(self.rfile)
            print("Received: {}, {}".format(header.pkt_type, header.payload_len))
            pkt_data = self.rfile.read(header.payload_len)

            local_proto.handle(header, pkt_data, self.wfile)

def serve_unix_thread():
    SOCKET_FILE = "/tmp/nofs.socket"
    if os.path.exists(SOCKET_FILE):
        # TODO: check if server is already running
        os.remove(SOCKET_FILE)

    def run_thread():
        server = NoFSUnixServer(SOCKET_FILE, NoFSUnixHandler)
        print("Starting Unix sockets server")
        server.serve_forever()

    th = threading.Thread(target=run_thread)
    th.daemon = True
    th.start()
    return th
