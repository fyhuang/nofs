import struct

_fmt = '!LL' # length, checksum(?)
size = struct.calcsize(_fmt)

def enum_from_value(enumtype, value):
    for v in enumtype.values:
        if v.number == value:
            return v.name
    return None

def make(size, cs):
    return struct.pack(_fmt, size, cs)

def parse(hdata):
    return struct.unpack(_fmt, hdata)
