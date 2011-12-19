import connect

try:
    sock = connect.connect()
    #sock.send(b'{"action":"stat", "bundle":"inbox/", "filepath":"/testdir/pic.jpg"}')
    sock.send(b'{"action":"index", "bundle":"inbox"}')
    print(sock.recv(1024))
finally:
    sock.close()
