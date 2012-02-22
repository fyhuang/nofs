import os.path
from bottle import route, run, request, HTTPError

import storage

PAGE_TEMPLATE = """<!DOCTYPE html>
<html>
<head><title>{title}</title></head>
<body>{body}</body>
</html>"""

@route('/admin')
def admin():
    return PAGE_TEMPLATE.format(title="Admin interface", body="""<form method="POST" action="/admin/add_file">
    <input type="text" name="filename" placeholder="Filename" />
    <input type="submit" value="Submit" />
</form>""")

@route('/admin/add_file', method='POST')
def add_file():
    fname = request.forms.filename
    if os.path.exists(fname):
        storage.store_file(sd, fname)
        return {"status": "done"}
    return HTTPError()

@route('/admin/list_files')
def list_files():
    d = {}
    with sd.storage_lock:
        for (k,v) in sd.file_index.items():
            d[repr(k)] = len(v.versions)
    return d

import threading

sd = None
def serve_http_thread(host, port, this_sd):
    global sd
    sd = this_sd

    def run_thread():
        sd.local.conn = storage.get_connection()
        run(host=host, port=port)

    th = threading.Thread(target=run_thread)
    th.daemon = True
    th.start()
    return th
