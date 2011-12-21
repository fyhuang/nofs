import os.path
import struct

import config
import bundle
import packet

def do_read_action(header, rfile, wfile):
    (bundle_len, fp_len) = struct.unpack('!HH', rfile.read(4))
    if bundle_len == 0:
        return packet.EBADPACKET

    bundle_name = rfile.read(bundle_len).decode()
    b = bundle.Bundle(bundle_name)
    if not b.valid():
        return packet.ENOBUNDLE

    if fp_len == 0:
        return packet.EBADPACKET

    raw_fp = rfile.read(fp_len).decode()
    fullpath = b.path_to(raw_fp)
    print("read: {0}, {1}".format(bundle_name, raw_fp))

    if fullpath is None:
        return packet.ENOFILE
    elif os.path.isdir(fullpath):
        # TODO: another error would probably be more appropriate
        return packet.EWRONGTYPE
    elif os.path.isfile(fullpath):
        with open(fullpath, 'rb') as f:
            contents = f.read()

            rs = config.MAX_RESPONSE_SIZE
            # round up
            num_packets = (len(contents) + rs - 1) // rs

            for i in range(num_packets):
                end_index = rs*(i+1)
                if end_index > len(contents):
                    end_index = len(contents)
                data = contents[rs*i:end_index]

                rh = packet.Header("response", packet.SUCCESS, header.req_id, len(data), num_packets, i+1) # TODO: i+1?
                wfile.write(rh.to_binary())
                wfile.write(data)
    else:
        return packet.EWRONGTYPE
