import packet

class AuthHandshake(object):
    def __init__(self, node):
        self.node = node
        self.req_id = random.randrange(2**16, 2**32)
        self.nonce = b''

    def get_nonce(self):
        h = packet.Header("request", packet.AUTH, self.req_id, 0)
        self.node.wstr.write(h.to_binary())
        h = packet.Header.from_stream(self.node.rstr)
