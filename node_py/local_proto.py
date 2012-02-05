import io
import os
import os.path
import struct
import socket
import stat
import time

import config

pkt_types = {
        'REQ_STAT': 1,
        'REQ_LISTDIR': 2,
        'REQ_READ': 3,

        'RESP_ERROR': 0,

        'RESP_STAT': 128,
        'RESP_LISTDIR': 129,
        'RESP_READ': 130,
        }
for k,v in pkt_types.items():
    globals()[k] = v

errors = {
        'ENOENT': 0,
        'EUNKNOWN': -1,
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

    def from_stream(s):
        bdata = s.read(Header.bsize)
        (pt, pl) = struct.unpack(Header.bfmt, bdata)
        return Header(pt, pl)

class ReqStat(object):
    def __init__(self, filepath):
        self.filepath = filepath
    def from_buffer(data):
        #(pl,) = struct.unpack("=L", data[:4])
        bpath = data[4:]
        return ReqStat(bpath.decode())

class ReqListdir(object):
    def __init__(self, dirpath):
        self.dirpath = dirpath
    def from_buffer(data):
        #(pl,) = struct.unpack("=L", socket.recv(4, socket.MSG_WAITALL))
        bpath = data[4:]
        return ReqListdir(bpath.decode())

class ReqRead(object):
    def __init__(self, filepath, offset, length):
        self.filepath = filepath
        self.offset = offset
        self.length = length
    def from_buffer(data):
        (ro, rl, pl) = struct.unpack_from("=QLL", data)
        bpath = data[16:]
        return ReqRead(bpath.decode(), ro, rl)

class RespStat(object):
    bfmt = "=cBxxLQQ"
    bsize = struct.calcsize(bfmt)
    def __init__(self, ftype, perms, inode, size, ctime_utc):
        self.ftype = ftype
        self.perms = perms
        self.inode = inode
        self.size = size
        self.ctime_utc = ctime_utc
    def to_binary(self):
        return struct.pack(RespStat.bfmt, self.ftype, self.perms, self.inode, self.size, self.ctime_utc)

class RespListdir(object):
    def __init__(self, entries):
        self.entries = entries
    def to_binary(self):
        bio = io.BytesIO()
        bio.write(struct.pack("=L", len(self.entries)))
        for e in self.entries:
            fp_bin = e[0].encode()
            bio.write(struct.pack("=L", len(fp_bin)))
            bio.write(fp_bin)
            bio.write(e[1].to_binary())
        return bio.getvalue()



################################
# Handlers

def handle(header, data, wfile):
    if header.pkt_type == REQ_STAT:
        packet = ReqStat.from_buffer(data)
        handler = handle_stat
    elif header.pkt_type == REQ_LISTDIR:
        packet = ReqListdir.from_buffer(data)
        handler = handle_listdir
    elif header.pkt_type == REQ_READ:
        packet = ReqRead.from_buffer(data)
        handler = handle_read
    else:
        # TODO: send error
        pass

    error = handler(packet, wfile)
    if error is not None:
        Header(RESP_ERROR, 4).to_stream(wfile)
        wfile.write(struct.pack("=l", error))

def do_stat(fp):
    try:
        stat_res = os.stat(fp)
    except OSError:
        print("Couldn't stat", fp)
        return None

    ctime_loc = stat_res.st_ctime
    ctime_utc = int(time.mktime(time.gmtime(ctime_loc)))

    if stat.S_ISREG(stat_res.st_mode):
        ftype = b'f'
    elif stat.S_ISDIR(stat_res.st_mode):
        ftype = b'd'
    else:
        print("Isn't file or dir", fp)
        return None
    return RespStat(ftype, 0, stat_res.st_ino, stat_res.st_size, ctime_utc)

def handle_stat(packet, wfile):
    fp = os.path.join(config.DATA_DIR, packet.filepath[1:])
    sr = do_stat(fp)
    if sr is None:
        return errors["ENOENT"]

    Header(RESP_STAT, RespStat.bsize).to_stream(wfile)
    wfile.write(sr.to_binary())

def handle_listdir(packet, wfile):
    dp = os.path.join(config.DATA_DIR, packet.dirpath[1:])
    print(dp)
    entries = []
    """
    for (dirpath, dirnames, filenames) in os.walk(dp):
        for f in filenames + dirnames:
            fp = os.path.join(dirpath, f)
            tp = fp[len(config.DATA_DIR):]
            sr = do_stat(fp)
            entries.append((tp, sr))
    """
    for f in os.listdir(dp):
        fp = os.path.join(dp, f)
        sr = do_stat(fp)
        entries.append((f, sr))

    bdata = RespListdir(entries).to_binary()
    Header(RESP_LISTDIR, len(bdata)).to_stream(wfile)
    wfile.write(bdata)

def handle_read(packet, wfile):
    fp = os.path.join(config.DATA_DIR, packet.filepath[1:])
    with open(fp, 'rb') as f:
        f.seek(packet.offset)
        bdata = f.read(packet.length)

    Header(RESP_READ, len(bdata)).to_stream(wfile)
    wfile.write(bdata)
