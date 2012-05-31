import socket
import select
try:
    import socketserver
except ImportError:
    import SocketServer as socketserver

from network.deferred_socket import DeferredSock
from network.peernode import PeerNode
from network import header

from proto import nofs_pb2

class RoutedNetwork(object):
    def __init__(self, port=12345):
        self.sock_to_peer = {}
        self.sock_to_conn = {}
        self.to_disconnect = []

        self.server_sock = socket.socket(socket.AF_INET)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind(('0.0.0.0', port))
        self.server_sock.listen(5)
        self.server_sock.setblocking(1)
        print("Server listening on 0.0.0.0:{}".format(port))

    def getsocks(self):
        yield self.server_sock
        for s in self.sock_to_conn.iterkeys():
            yield s

    def process(self, timeout=0.0):
        # Get connections
        #print("Processing")
        #try:
            (reads, writes, xcepts) = select.select(self.getsocks(), [], [], timeout)
            for sock in reads:
                if sock is self.server_sock:
                    self._accept()
                else:
                    self._handle(sock)
        #except:
            #print("Exception, shutting down")
            #self.server_sock.shutdown(socket.SHUT_RDWR)
            #self.server_sock.close()

        for c in self.to_disconnect:
            self._disconnect(c.sock)
        self.to_disconnect = []

    def _accept(self):
        try:
            (sock, addr) = self.server_sock.accept()
        except socket.error:
            print("Error accepting")
            return
        conn = DeferredSock(sock)
        self.sock_to_conn[sock] = conn
        self.sock_to_peer[sock] = PeerNode(conn, addr)
        self.phead[sock] = None
        print("Accepting connection from {}".format(addr))
        print("Peers now {}".format(self.sock_to_peer))

    def _handle(self, sock):
        conn = self.sock_to_conn[sock]
        peer = self.sock_to_peer[sock]
        if not peer.isinit:
            if not peer.init():
                self._disconnect(sock)
        else:
            pdata = peer.getpacket()
            if pdata is None: return
            # TODO: parse packet
            print(pdata)

    def disconnect(self, conn):
        self.to_disconnect.append(conn)

    def _disconnect(self, sock):
        print("Disconnected peer {}".format(self.sock_to_peer[sock]))
        del self.sock_to_conn[sock]
        del self.sock_to_peer[sock]
        print("Peers now {}".format(self.sock_to_peer))

    def broadcast(self, message):
        for p in self.sock_to_peer.itervalues():
            p.sendmsg(message)

    def connectto(self, peeraddr):
        sock = socket.socket(socket.AF_INET)
        sock.connect(peeraddr)
        #self.broadcast(
        sock.send(b'DNODE')
        
        conn = DeferredSock(sock)
        peer = PeerNode(conn, peeraddr)
        self.sock_to_conn[sock] = conn
        self.sock_to_peer[sock] = peer

        # Send a greeting
        pa = nofs_pb2.PeerAnnounce()
        pa.name = 'localhost'
        pa.version = '0.1'
        pa.proto_version = 1
        peer.sendmsg(pa)

        print("Connected to {}".format(peeraddr))
