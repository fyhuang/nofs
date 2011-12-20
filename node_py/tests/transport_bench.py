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
            print("Read contents")

            fmt = "!BxxxI{0}s".format(len(contents))
            packet = struct.pack(fmt, 0, len(contents), contents)
            self.wfile.write(packet)

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

        contents_enc = sf.read(length)
        (contents) = struct.unpack("{0}s".format(length), contents_enc)

        print(contents[0][:512])
    finally:
        sock.close()
        sf.close()

if sys.argv[1] == 'serve':
    serve_unix()
else:
    test_unix()
