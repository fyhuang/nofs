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
        for d in dirnames:
            full_path = os.path.join(dirpath, d)
            trunc_path = full_path[len(b.path):].encode()

            buf.write(struct.pack("!H", len(trunc_path)))
            buf.write(trunc_path)
            buf.write(struct.pack("!xxxc", b'd'))

            num_entries += 1
        for f in filenames:
            full_path = os.path.join(dirpath, f)
            trunc_path = full_path[len(b.path):].encode()

            buf.write(struct.pack("!H", len(trunc_path)))
            buf.write(trunc_path)
            buf.write(struct.pack("!xxxc", b'f'))

            num_entries += 1

    payload = buf.getvalue()
    rh = packet.Header("response", packet.SUCCESS, header.req_id, len(payload) + 4)
    wfile.write(rh.to_binary())
    wfile.write(struct.pack("!I", num_entries))
    wfile.write(payload)
