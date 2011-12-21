import struct

actions = {'STAT': 1, 'INDEX': 2, 'READ': 3, 'STOP': 255}
action_ixs = {v:k for (k,v) in actions.items()}
for k,v in actions.items():
    globals()[k] = v

resultcodes = {
    'SUCCESS': 0,
    'EUNKNOWN': 255,
    'EBADPACKET': 254,
    'EINVACTION': 253,
    'ENOBUNDLE': 252,
    'ENOFILE': 251,
    }
resultcode_ixs = {v:k for (k,v) in resultcodes.items()}
for k,v in resultcodes.items():
    globals()[k] = v

class Header(object):
    binary_fmt = "!3sBII"
    binary_fmt_size = struct.calcsize(binary_fmt)

    def __init__(self, pkt_type, code, req_id, payload_len):
        self.pkt_type = pkt_type
        self.code = code
        self.req_id = req_id
        self.payload_len = payload_len

    def __str__(self):
        if self.pkt_type == "request":
            decoded = action_ixs[self.code]
        else:
            decoded = resultcode_ixs[self.code]

        return "{0}: {1} (id {2}), len {3}".format(
                self.pkt_type,
                decoded,
                self.req_id,
                self.payload_len)

    def from_binary(data):
        (magic, code, rid, plen) = struct.unpack(Header.binary_fmt, data)
        if magic == b'NFQ':
            pt = "request"
        elif magic == b'NFR':
            pt = "response"
        else:
            return None

        return Header(pt, code, rid, plen)

    def to_binary(self):
        if self.pkt_type == "request":
            magic = b'NFQ'
        else:
            magic = b'NFR'
        return struct.pack(Header.binary_fmt, magic, self.code, self.req_id, self.payload_len)

def make_error(code, rid):
    return Header("response", code, rid, 0)

