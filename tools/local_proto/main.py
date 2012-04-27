import sys
import socket
import struct
import cmd

import nofs_local_pb2 as nofs_local
from nofs_local_pb2 import *

def enum_from_value(enumtype, value):
    for v in enumtype.values:
        if v.number == value:
            return v.name
    return None

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
        return "{0} ({1})".format(enum_from_value(nofs_local._MESSAGETYPE, self.pkt_type), self.payload_len)

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
            print("Error: {}".format(enum_from_value(nofs_local._ERRORCODE, ecode)))
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
        send_packet(REQ_STAT, packet)
        recv_and_print(RespStat)

    def do_listdir(self, line):
        packet = ReqListdir()
        packet.dirpath = line
        send_packet(REQ_LISTDIR, packet)
        recv_and_print(RespListdir)

    def do_read(self, line):
        packet = ReqListdir()

    def do_addfile(self, line):
        packet = AReqAddFile()
        packet.ext_filepath = line
        packet.destdir = ''
        send_packet(REQ_ADM_ADDFILE, packet)
        recv_and_print(ARespAddFile)

    def do_exit(self, line):
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        return True

c = LocalProtoCmd()
c.cmdloop()
