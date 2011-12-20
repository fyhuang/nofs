from socketserver import *
import os
import os.path
import sys
import base64
import struct

sys.path.append('.')
sys.path.append('../..')
import connect
from node_py import json_segment

class TestUnixServer(UnixStreamServer):
    pass

class TestUnixHandler(StreamRequestHandler):
    def handle(self):
        print("Received request")
        with open('files/inbox/testdir/pic.jpg', 'rb') as f:
            contents = f.read()
            encoded = base64.b64encode(contents)
            print("Read contents")

            fmt = "!BxxxI"
            packet = struct.pack(fmt, 0, len(encoded))
            self.wfile.write(packet)
            self.wfile.write(encoded)

            print("Successfully sent")

def serve_unix():
    SOCKET_FILE = "/tmp/nofs.socket"
    if os.path.exists(SOCKET_FILE):
        # TODO: check if server is already running
        os.remove(SOCKET_FILE)
    server = TestUnixServer(SOCKET_FILE, TestUnixHandler)
    print("Starting Unix sockets server")
    server.serve_forever()

def test_unix():
    try:
        sock = connect.connect()
        sf = sock.makefile('rb', 4096)

        header_fmt = "!BxxxI"
        size = struct.calcsize(header_fmt)
        header = sf.read(size)
        (result, length) = struct.unpack(header_fmt, header)

        contents = sf.read(length)

        print(base64.b64encode(contents[:512]))
    finally:
        sock.close()
        sf.close()

if sys.argv[1] == 'serve':
    serve_unix()
else:
    test_unix()
