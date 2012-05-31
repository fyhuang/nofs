class DeferredSock(object):
    """Wrapper for easy async sockets.
    Allows waiting for certain amount of data to come in.
    """

    def __init__(self, sock, timeout=1.0):
        self.sock = sock
        #self.sock.settimeout(timeout)
        self.buffer = b''

    def readall(self, size):
        print("Trying to perform read of size {}".format(size))
        if len(self.buffer) >= size:
            print("Buffer already has data")
            data = self.buffer[:size]
            self.buffer = self.buffer[size:]
            return data

        try:
            toread = size - len(self.buffer)
            print("Reading {}".format(toread))
            data = self.sock.recv(toread)
            if len(data) == 0:
                return []
            self.buffer += data
            print("Received {} (buffer now {})".format(data, self.buffer))
            if len(self.buffer) == size:
                data = self.buffer
                self.buffer = b''
                return data
        except socket.timeout:
            return None

    def send(self, data):
        return self.sock.send(data)


