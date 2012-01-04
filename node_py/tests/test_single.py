import sys
import io
import struct

sys.path.append('..')
import connect
import packet

try:
    sock = connect.connect()

    bundle = "inbox".encode()
    filepath = "testdir/pic.jpg".encode()
    header = packet.Header("request", packet.INDEX, 0, len(bundle)+4)# + len(filepath) + 4)
    sock.send(header.to_binary())
    sock.send(struct.pack("!HH", len(bundle), len(filepath)))
    sock.send(bundle)
    #sock.send(filepath)

    #f = open('data', 'wb')

    ix = 0
    num_packets = 1
    while ix < num_packets:
        header_raw = sock.recv(packet.Header.binary_fmt_size)
        header = packet.Header.from_binary(header_raw)
        print(header)

        if header.code == packet.SUCCESS:
            num_packets = header.total_pkts
            payload = sock.recv(header.payload_len)
            #f.write(payload)

        ix += 1

    #f.close()

    #print(struct.unpack("!xxxc", packet))

    pio = io.BytesIO(payload)
    num_entries = struct.unpack("!I", pio.read(4))[0]
    for i in range(num_entries):
        name_len = struct.unpack("!H", pio.read(2))[0]
        name = pio.read(name_len).decode()
        print(name)
        print(struct.unpack("!xxxc", pio.read(4)))

finally:
    sock.close()
    #sf.close()
