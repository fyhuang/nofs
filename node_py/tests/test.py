#!/usr/bin/python
import socket
import sys

print(sys.version_info)
if sys.version_info[0] < 3:
    print("This program requires Python 3")
    sys.exit()

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

try:
    sock.connect("/tmp/nofs.socket")
    while True:
        print("Enter some data:")
        data = sys.stdin.readline()
        sock.send(data.encode())

        received = sock.recv(1024)
        print(received)
finally:
    sock.close()
