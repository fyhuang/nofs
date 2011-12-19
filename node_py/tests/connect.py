import socket

def connect():
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect("/tmp/nofs.socket")
    return sock
