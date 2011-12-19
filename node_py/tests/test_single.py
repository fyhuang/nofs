import connect

try:
    sock = connect.connect()
    sock.send(b'{"action":"index"}')
    print(sock.recv(1024))
finally:
    sock.close()
