from network import header

class PeerNode(object):
    def __init__(self, network, conn, addr):
        self.network = network
        self.conn = conn
        self.addr = addr

        self.isinit = False
        self.protocol = None
        self.name = None

        self.currheader = None

    def init(self):
        """ returns True if nothing has gone wrong so far"""
        print("Initializing")
        if self.protocol is None:
            proto = self.conn.readall(5)
            if proto is None: return
            if proto in [b'DNODE', b'LOCAL']:
                print("Setting protocol to {}".format(proto))
                self.protocol = proto
                self.isinit = True
            else:
                print("Wrong proto")
                return False
        return True
    
    def connect(self):
        pass

    def sendmsg(self, msg):
        data = msg.SerializeToString()
        h = header.make(len(data), 0)
        self.conn.send(h)
        self.conn.send(data)

    def getpacket(self):
        if self.currheader is None:
            hdata = self.conn.readall(header.size)
            if hdata is None: return None
            if len(hdata) == 0:
                self.network.disconnect(self.conn)
                return None
            self.currheader = header.parse(hdata)

        if self.currheader is not None:
            pdata = self.conn.readall(self.currheader[0])
            if pdata is None: return None
            if len(pdata) == 0:
                self.network.disconnect(self.conn)
                return None

            return pdata


