import sys
import io
import struct

sys.path.append('../..')
import connect
from node_py import packet

try:
    sock = connect.connect()

    bundle = "inbox".encode()
    filepath = "test.txt".encode()
    header = packet.Header("request", packet.STAT, 0, len(bundle) + len(filepath) + 4)
    sock.send(header.to_binary())
    sock.send(struct.pack("!HH", len(bundle), len(filepath)))
    sock.send(bundle)
    sock.send(filepath)

    header_raw = sock.recv(packet.Header.binary_fmt_size)
    header = packet.Header.from_binary(header_raw)
    print(header)

    if header.code == packet.SUCCESS:
        packet = sock.recv(header.payload_len)
        print(struct.unpack("!xxxc", packet))

finally:
    sock.close()
    #sf.close()
