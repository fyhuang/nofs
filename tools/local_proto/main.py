import sys
import socket
import struct
import cmd

from nofs_local_pb2 import *

pkt_types = {
        'REQ_STAT': 1,
        'REQ_LISTDIR': 2,
        'REQ_READ': 3,

        'RESP_ERROR': 0,

        'RESP_STAT': 128,
        'RESP_LISTDIR': 129,
        'RESP_READ': 130,


        'REQ_ADM_ADDFILE': 64,
        'RESP_ADMIN': 192,
        }

class Header(object):
    bfmt = "=LL"
    bsize = struct.calcsize(bfmt)

    def __init__(self, pkt_type, payload_len):
        self.pkt_type = pkt_type
        self.payload_len = payload_len

    def to_stream(self, s):
        bdata = struct.pack(Header.bfmt, self.pkt_type, self.payload_len)
        s.write(bdata)

    @staticmethod
    def from_stream(s):
        bdata = s.read(Header.bsize)
        (pt, pl) = struct.unpack(Header.bfmt, bdata)
        return Header(pt, pl)

    def __str__(self):
        return "{0} ({1})".format(self.pkt_type, self.payload_len)

target = sys.argv[1]

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.connect(target)
sock.send("LOCAL")
rfile = sock.makefile('rb')
wfile = sock.makefile('wb')

def send_packet(ptype, pbuf):
    ser = pbuf.SerializeToString()
    h = Header(ptype, len(ser))
    h.to_stream(wfile)
    wfile.write(ser)
    wfile.flush()

def recv_and_print(klass):
    h = Header.from_stream(rfile)
    print(h)
    if h.payload_len > 0:
        if h.pkt_type == 0:
            (ecode,) = struct.unpack('=l', rfile.read(h.payload_len))
            print("Error: {}".format(ecode))
        else:
            data = rfile.read(h.payload_len)
            pbuf = klass()
            pbuf.ParseFromString(data)
            print(pbuf)
    else:
        print("(No response body)")

class LocalProtoCmd(cmd.Cmd):
    def do_stat(self, line):
        packet = ReqStat()
        packet.filepath = line
        send_packet(pkt_types['REQ_STAT'], packet)
        recv_and_print(RespStat)

    def do_listdir(self, line):
        packet = ReqListdir()
        packet.dirpath = line
        send_packet(pkt_types['REQ_LISTDIR'], packet)
        recv_and_print(RespListdir)

    def do_read(self, line):
        packet = ReqListdir()

    def do_exit(self, line):
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        return True

c = LocalProtoCmd()
c.cmdloop()
