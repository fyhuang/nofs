from ctypes import *
import os.path
import inspect
import struct

HERE=os.path.dirname(inspect.getfile(inspect.currentframe()))
FILENAME=os.path.join(HERE, 'cblockify_lib/libcblockify.dylib')
print(FILENAME)

if not os.path.exists(FILENAME):
    print("Couldn't find cblockify library")
    raise ImportError()

dll = CDLL(FILENAME)

try:
    dll.beginBlockify.restype = c_void_p
    dll.beginBlockify.argtypes = [c_char_p,]
    dll.nextBlock.restype = c_int
    dll.nextBlock.argtypes = [c_void_p, c_char_p,]
    dll.endBlockify.argtypes = [c_void_p,]
except AttributeError:
    print("Couldn't find required functions")
    raise ImportError()

def blocklist(filename):
    bt = dll.beginBlockify(filename.encode())
    if bt is None:
        return None

    blocks = []
    retval = create_string_buffer(8 + (256//8))
    cont = dll.nextBlock(bt, retval)
    while cont == 0:
        (bpos,) = struct.unpack_from('=Q', retval.raw)
        blocks.append(bpos)
        cont = dll.nextBlock(bt, retval)

    dll.endBlockify(bt)
    return blocks
