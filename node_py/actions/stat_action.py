import os
import os.path
import struct

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
        fullpath = b.path_to(raw_fp)
        if fullpath is None:
            return packet.ENOFILE
        elif os.path.isdir(fullpath):
            rh = packet.Header("response", packet.SUCCESS, header.req_id, 4)
            wfile.write(rh.to_binary())
            wfile.write(struct.pack("!xxxc", b'd'))
        elif os.path.isfile(fullpath):
            stat_res = os.stat(fullpath)

            rh = packet.Header("response", packet.SUCCESS, header.req_id, 4)
            wfile.write(rh.to_binary())
            wfile.write(struct.pack("!xxxc", b'f'))
        else:
            return packet.ENOFILE
    else:
        rh = packet.Header("response", packet.SUCCESS, header.req_id, 4)
        wfile.write(rh.to_binary())
        wfile.write(struct.pack("!xxxc", b'b'))

