from os.path import *

import config

def do_stat_action(request):
    bundle_name = request['bundle']
    if len(bundle_name) == 0:
        return {'result': 'no bundle', 'resultcode': 2}
    b = bundle.Bundle(bundle_name)
    if not b.valid():
        return {'result': 'not a bundle', 'resultcode': 3}

    if 'filepath' in request:
        fullpath = b.path_to_file(request['filepath'])
    else:
        return {'result': 'success',
                'resultcode': 0,
                'filetype': 'bundle',
                'filesize': 0}

