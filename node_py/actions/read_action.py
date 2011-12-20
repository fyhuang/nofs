import os.path
import base64
import math

import config
import bundle
import errors

def split_read_response(contents):
    rs = config.MAX_RESPONSE_SIZE
    # round up
    num_packets = (len(contents) + rs - 1) // rs

    yield {'result': 'success',
           'resultcode': 0,
           'multipart': True,
           'numparts': num_packets}

    for i in range(num_packets):
        end_index = rs*(i+1)
        if end_index > len(contents):
            end_index = len(contents)
        data_str = base64.b64encode(contents[rs*i:end_index]).decode()
        yield {'result': 'continued',
               'partnum': i,
               'contents': data_str}

def do_read_action(request):
    bundle_name = request['bundle']
    if len(bundle_name) == 0:
        return errors.Responses.BADPACKET
    if not 'filepath' in request:
        return errors.Responses.BADPACKET

    b = bundle.Bundle(bundle_name)
    if not b.valid():
        return errors.Responses.NOBUNDLE

    fullpath = b.path_to(request['filepath'])
    if fullpath is None:
        return errors.Responses.NOFILE
    elif os.path.isdir(fullpath):
        # TODO: another error would probably be more appropriate
        return errors.Responses.BADPACKET
    elif os.path.isfile(fullpath):
        with open(fullpath, 'rb') as f:
            # TODO: what about super large files?
            contents = f.read()
            if len(contents) > config.MAX_RESPONSE_SIZE:
                return split_read_response(contents)
            return {'result': 'success',
                    'resultcode': 0,
                    'contents': base64.b64encode(contents).decode()}
    else:
        return errors.Responses.NOFILE
