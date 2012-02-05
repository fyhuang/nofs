# Contains functions for determining the network protocol.

def determine(stream):
    ch = stream.read(1)
    if ch == b'L':
        st = stream.read(4)
        if st == b'OCAL':
            return 'local'
    elif ch == b'N':
        st = stream.read(3)
        if st == b'ODE':
            return 'node'
    return None
