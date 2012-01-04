import os
import os.path
import struct
import stat
import time

import config
import bundle
import packet

def do_stat_action(header, rfile, wfile):
    (bundle_len, fp_len) = struct.unpack('!HH', rfile.read(4))
    if bundle_len == 0:
        return packet.EBADPACKET

    print("path lengths: {0}, {1}".format(bundle_len, fp_len))

    bundle_name = rfile.read(bundle_len).decode()
    b = bundle.Bundle(bundle_name)
    if not b.valid():
        return packet.ENOBUNDLE

    if fp_len > 0:
        raw_fp = rfile.read(fp_len).decode()
        print("stat: {0}, {1}".format(bundle_name, raw_fp))
        sr = b.stat(raw_fp)
        if sr is None:
            return packet.ENOFILE

        rh = packet.Header("response", packet.SUCCESS, header.req_id, packet.StatResponse.binary_size)
        wfile.write(rh.to_binary())
        wfile.write(sr.to_binary())
    else:
        rh = packet.Header("response", packet.SUCCESS, header.req_id, packet.StatResponse.binary_size)
        wfile.write(rh.to_binary())

        sr = packet.StatResponse(b'b', 0, 0)
        wfile.write(sr.to_binary())

