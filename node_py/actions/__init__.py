import os.path

import config
import packet
from actions import stat_action, index_action, read_action

def handle(header, rfile, wfile):
    action = header.code
    if action == packet.STAT:
        err = stat_action.do_stat_action(header, rfile, wfile)
    elif action == packet.INDEX:
        err = index_action.do_index_action(header, rfile, wfile)
    elif action == packet.READ:
        err = read_action.do_read_action(header, rfile, wfile)
    elif action == packet.STOP:
        return False
    else:
        print("invalid action!")
        wfile.write(packet.make_error(packet.EINVACTION, header.req_id).to_binary())

    if err is not None:
        print("sending error {0}".format(packet.resultcode_ixs[err]))
        wfile.write(packet.make_error(err, header.req_id).to_binary())
    return True
