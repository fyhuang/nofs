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


        'REQ_ADM_ADDFILE': 64,
        'RESP_ADM_ADDFILE': 192,
        }
for k,v in pkt_types.items():
    globals()[k] = v

errors = {
        'ENOENT': 0,
        'EBADPACKET': 1,
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

    @staticmethod
    def from_stream(s):
        bdata = s.read(Header.bsize)
        (pt, pl) = struct.unpack(Header.bfmt, bdata)
        return Header(pt, pl)
    
    def __str__(self):
        return "{0} ({1})".format(self.pkt_type, self.payload_len)

from proto.nofs_local_pb2 import *

################################
# Handlers

def handle(header, data, wfile):
    print(header)
    handler = None
    if header.pkt_type == REQ_STAT:
        packet = ReqStat()
        handler = handle_stat
    elif header.pkt_type == REQ_LISTDIR:
        packet = ReqListdir()
        handler = handle_listdir
    elif header.pkt_type == REQ_READ:
        packet = ReqRead()
        handler = handle_read
    elif header.pkt_type == REQ_ADM_ADDFILE:
        packet = ReqAdmAddfile()
        handler = handle_adm_addfile
    else:
        print("Unrecognized packet type: {}".format(header.pkt_type))
        error = EBADPACKET

    packet.ParseFromString(data)
    if handler is not None:
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
        ftype = stat.S_IFREG
    elif stat.S_ISDIR(stat_res.st_mode):
        ftype = stat.S_IFDIR
    else:
        print("Isn't file or dir", fp)
        return None

    rs = RespStat()
    rs.ftype = ftype
    rs.perms = 0
    rs.inode = stat_res.st_ino
    rs.size = stat_res.st_size
    rs.ctime_utc = ctime_utc
    return rs

def handle_stat(packet, wfile):
    fp = os.path.join(config.DATA_DIR, packet.filepath[1:])
    sr = do_stat(fp)
    if sr is None:
        return errors["ENOENT"]

    ser = sr.SerializeToString()
    Header(RESP_STAT, len(ser)).to_stream(wfile)
    wfile.write(ser)

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

def handle_adm_addfile(packet, wfile):
    fname = packet.filepath
    if not os.path.exists(fname):
        return ENOENT
    storage.store_file(sd, fname)
