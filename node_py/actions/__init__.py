import os.path

import config

def handle(request):
    try:
        action = request['action']
        if action == 'stat':
            return do_stat_action(request)
        elif action == 'index':
            return {'result': 'error'}
        elif action == 'stop':
            return False
        else:
            return {'result': 'Unrecognized action', 'resultcode': 1}
    except KeyError:
        return {'result': 'Malformed request', 'resultcode': 1}

    return {'result': "Unknown error", 'resultcode': -1}
