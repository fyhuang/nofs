import os
import os.path

import config
import bundle
import errors

def do_index_action(request):
    bundle_name = request['bundle']
    if len(bundle_name) == 0:
        return errors.Responses.BADPACKET

    b = bundle.Bundle(bundle_name)
    if not b.valid():
        return errors.Responses.NOBUNDLE

    # TODO: index only works on bundles?
    index_entries = []
    for (dirpath, dirnames, filenames) in os.walk(b.path):
        for d in dirnames:
            full_path = os.path.join(dirpath, d)
            index_entries.append(full_path[len(b.path):])
        for f in filenames:
            full_path = os.path.join(dirpath, f)
            index_entries.append(full_path[len(b.path):])

    return {'result': 'success',
            'resultcode': 0,
            'index': index_entries}
