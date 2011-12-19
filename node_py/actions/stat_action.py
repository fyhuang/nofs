import os
import os.path

import config
import errors

def do_stat_action(request):
    bundle_name = request['bundle']
    if len(bundle_name) == 0:
        return errors.Responses.BADPACKET

    b = bundle.Bundle(bundle_name)
    if not b.valid():
        return errors.Responses.NOBUNDLE

    if 'filepath' in request:
        fullpath = b.path_to_file(request['filepath'])
        if os.path.isdir(fullpath):
            return {'result': 'success',
                    'resultcode': 0,
                    'filetype': 'directory',
                    'filesize': 0}
        elif os.path.isfile(fullpath):
            stat_res = os.stat(fullpath)
            return {'result': 'success',
                    'resultcode': 0,
                    'filetype': 'file',
                    'filesize': stat_res.st_size}
        else:
            return errors.Responses.NOFILE
    else:
        return {'result': 'success',
                'resultcode': 0,
                'filetype': 'bundle',
                'filesize': 0}

