import socket
import sys

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

try:
    sock.connect("/tmp/nofs.socket")
    while True:
        print("Enter some data:")
        data = sys.stdin.readline()
        sock.send(data)

        received = sock.recv(1024)
        print(received)
finally:
    sock.close()
