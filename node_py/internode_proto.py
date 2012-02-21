# Packets for the internode protocol

import socket
import struct

class Header(object):
    bfmt = "!LLL"
    bsize = struct.calcsize(bfmt)

    def __init__(self, pkt_type, payload_len, checksum):
        self.pkt_type = pkt_type
        self.payload_len = payload_len
        self.checksum = checksum
    def from_buf(b):
        (pt, pl, ck) = struct.unpack_from(Header.bfmt, b)
        return Header(pt, pl, ck)
    def to_stream(self, s):
        bdata = struct.pack(Header.bfmt,
                    self.pkt_type,
                    self.payload_len,
                    self.checksum)
        s.write(bdata)

def recv_packet_into(sock, buf):
    hbuf = sock.recv(Header.bsize, socket.MSG_WAITALL)
    if hbuf is None or len(hbuf) < Header.bsize:
        return None

    h = Header.from_buf(hbuf)
    bytes_read = sock.recv_into(buf, h.payload_len, socket.MSG_WAITALL)
    if bytes_read < h.payload_len:
        return None

    return h

def check_packet(h, buf):
    # TODO: compute checksums
    pass
