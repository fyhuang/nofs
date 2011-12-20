import sys
import json
import base64
import io

sys.path.append('../..')
import connect
from node_py import json_segment

try:
    sock = connect.connect()
    #sock.send(b'{"action":"stat", "bundle":"inbox/", "filepath":"/testdir/pic.jpg"}')
    #sock.send(b'{"action":"index", "bundle":"inbox"}')
    sock.send(b'{"action":"read", "bundle":"inbox", "filepath":"testdir/pic.jpg"}')

    sf = sock.makefile('rb', 4096)
    packet = json_segment.next_json(sf)
    result = json.loads(packet.decode())
    print(result)
    if 'multipart' in result and result['multipart']:
        num_parts = result['numparts']

        with open('data', 'wb') as f:
            for i in range(num_parts):
                packet = json_segment.next_json(sf)
                #print("Part", i)
                result = json.loads(packet.decode())
                f.write(base64.b64decode(result['contents'].encode()))
finally:
    sock.close()
    sf.close()
