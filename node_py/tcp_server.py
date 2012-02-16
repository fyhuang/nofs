from socketserver import *

import select
import proto

def twoway(sock, initiator=True):
    if initiator:
        # TODO: send proto, intro packet
        pass
    else:
        # Read proto, intro packet
        other_proto = proto.determine(self.rfile)
        if client_proto not in ['internode']:
            return

    while True:
        # TODO: data queue for writing?
        (rready, wready, xready) = select.select([sock], [], [], 0)
        if len(rready) > 0:
            # TODO: Read one packet
            pass


class NoFSTCPServer(ThreadingMixIn, TCPServer):
    pass

class NoFSTCPHandler(StreamRequestHandler):
    def handle(self):
        return twoway(self.connection, False)

def serve_tcp(host, port, sd):
    server = NoFSTCPServer((host, port), NoFSTCPHandler)
    server.timeout = 5
    print("Starting TCP server on {},{}".format(host, port))
    while True:
        server.handle_request()
        # Check whether to quit
        with sd.state_lock:
            if not sd.running:
                return
