import os
import os.path
import io
import struct

import bundle
import packet

def do_index_action(header, rfile, wfile):
    bundle_len = struct.unpack('!Hxx', rfile.read(4))[0]
    if bundle_len == 0:
        return packet.EBADPACKET

    bundle_name = rfile.read(bundle_len).decode()
    b = bundle.Bundle(bundle_name)
    if not b.valid():
        return packet.ENOBUNDLE

    # TODO: index only works on bundles?
    num_entries = 0
    buf = io.BytesIO()
    for (dirpath, dirnames, filenames) in os.walk(b.path):
        for f in filenames + dirnames:
            full_path = os.path.join(dirpath, f)
            trunc_path = full_path[len(b.path):]
            tp_enc = trunc_path.encode()

            buf.write(struct.pack("!H", len(tp_enc)))
            buf.write(tp_enc)
            sr = b.stat(trunc_path)
            buf.write(sr.to_binary())

            num_entries += 1

    payload = buf.getvalue()
    rh = packet.Header("response", packet.SUCCESS, header.req_id, len(payload) + 4)
    wfile.write(rh.to_binary())
    wfile.write(struct.pack("!I", num_entries))
    wfile.write(payload)
