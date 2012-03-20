from ctypes import *
import os.path
import inspect

HERE=os.path.dirname(inspect.getfile(inspect.currentframe()))
FILENAME=os.path.join(HERE, 'cblockify_lib/libcblockify.dylib')
print(FILENAME)

if not os.path.exists(FILENAME):
    print("Couldn't find cblockify library")
    raise ImportError()

dll = CDLL(FILENAME)

try:
    dll.beginBlockify
    dll.nextBlock
    dll.endBlockify
except AttributeError:
    print("Couldn't find required functions")
    raise ImportError()

def blocklist(fd):
    bt = dll.beginBlockify(fd.fileno())
    if bt is None:
        return None

    blocks = []
    nb = dll.nextBlock(bt)
    while nb != 0:
        blocks.append(nb)
        nb = dll.nextBlock(bt)

    dll.endBlockify(bt)
    return blocks
