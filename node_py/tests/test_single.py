import sys
import io
import struct

sys.path.append('..')
import connect
import packet

try:
    sock = connect.connect()

    bundle = "inbox".encode()
    filepath = "".encode()
    header = packet.Header("request", packet.INDEX, 0, len(bundle) + len(filepath) + 4)
    sock.send(header.to_binary())
    sock.send(struct.pack("!Hxx", len(bundle)))#, len(filepath)))
    sock.send(bundle)
    #sock.send(filepath)

    header_raw = sock.recv(packet.Header.binary_fmt_size)
    header = packet.Header.from_binary(header_raw)
    print(header)

    if header.code == packet.SUCCESS:
        packet = sock.recv(header.payload_len)
        #print(struct.unpack("!xxxc", packet))

        pio = io.BytesIO(packet)
        num_entries = struct.unpack("!I", pio.read(4))[0]
        for i in range(num_entries):
            name_len = struct.unpack("!H", pio.read(2))[0]
            name = pio.read(name_len).decode()
            print(name)
            print(struct.unpack("!xxxc", pio.read(4)))

finally:
    sock.close()
    #sf.close()
