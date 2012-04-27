import io
import os
import os.path
import struct
import socket
import stat
import time

import config
import storage
import database

import proto.nofs_local_pb2 as nofs_local
from proto.nofs_local_pb2 import *

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

################################
# Handlers

def do_stat(fp):
    """try:
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
        return None"""

    stat_res = fp.stat()
    rs = RespStat()
    rs.ftype = stat.S_IFREG
    rs.perms = 0
    rs.inode = fp.fid
    rs.size = stat_res['size_bytes']
    rs.ctime_utc = stat_res['dt_utc']
    return rs

def handle_stat(packet, wfile):
    #fp = os.path.join(config.DATA_DIR, packet.filepath[1:])
    #sr = do_stat(fp)
    fp = storage.get_file(packet.filepath[1:])
    if fp is None:
        return ENOENT

    sr = do_stat(fp)
    ser = sr.SerializeToString()
    Header(RESP_STAT, len(ser)).to_stream(wfile)
    wfile.write(ser)

def handle_listdir(packet, wfile):
    dp = os.path.join(config.DATA_DIR, packet.dirpath[1:])
    print(dp)

    lr = RespListdir()
    with database.connect() as c:
        rows = c.execute('SELECT * FROM Files').fetchall()
        for f in rows:
            fp = storage.get_file(f[1])
            sr = do_stat(fp)

            le = lr.entry.add()
            le.filename = f[1]
            le.stat.CopyFrom(sr)

    ser = lr.SerializeToString()
    Header(RESP_LISTDIR, len(ser)).to_stream(wfile)
    wfile.write(ser)

def handle_read(packet, wfile):
    fp = os.path.join(config.DATA_DIR, packet.filepath[1:])
    with open(fp, 'rb') as f:
        f.seek(packet.offset)
        bdata = f.read(packet.length)

    Header(RESP_READ, len(bdata)).to_stream(wfile)
    wfile.write(bdata)

def handle_adm_addfile(packet, wfile):
    fname = packet.ext_filepath
    destdir = packet.destdir
    if not os.path.exists(fname):
        return ENOENT
    fid = storage.store_file_ext(fname, destdir)

    rs = ARespAddFile()
    rs.fid = fid
    ser = rs.SerializeToString()
    Header(RESP_ADM_ADDFILE, len(ser)).to_stream(wfile)
    wfile.write(ser)


pkt_type_to_type_handler = {
        REQ_STAT: (ReqStat, handle_stat),
        REQ_LISTDIR: (ReqListdir, handle_listdir),
        REQ_READ: (ReqRead, handle_read),

        REQ_ADM_ADDFILE: (AReqAddFile, handle_adm_addfile),
        }

def handle(header, data, wfile):
    print(header)

    if header.pkt_type not in pkt_type_to_type_handler:
        print("Unrecognized packet type: {}".format(header.pkt_type))
        error = EBADPACKET
    else:
        ptype, handler = pkt_type_to_type_handler[header.pkt_type]
        packet = ptype()
        packet.ParseFromString(data)
        error = handler(packet, wfile)

    if error is not None:
        Header(RESP_ERROR, 4).to_stream(wfile)
        wfile.write(struct.pack("=l", error))

