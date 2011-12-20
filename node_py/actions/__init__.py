import os.path

import config
from actions import stat_action, index_action, read_action

def handle(request):
    try:
        action = request['action']
        if action == 'stat':
            return stat_action.do_stat_action(request)
        elif action == 'index':
            return index_action.do_index_action(request)
        elif action == 'read':
            return read_action.do_read_action(request)
        elif action == 'stop':
            return None
        else:
            return {'result': 'Unrecognized action', 'resultcode': 1}
    except KeyError:
        return {'result': 'Malformed request', 'resultcode': 1}

    return {'result': "Unknown error", 'resultcode': -1}
