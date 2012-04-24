"""
A blocklist is a list of 16-MB chunks, each of which
is split into varying-size blocks. The structure
of a blocklist looks like:

[ # 16 MB "superblocks"
    [ # blocks
        (block_hash, block_size)
    ]
]
"""

import time
import os.path
import uuid
import hashlib
import struct
from contextlib import closing

import config
import shared
import database as db
try:
    import cblockify as bl
except ImportError:
    print("Warning: optimized blockify not found, using slow Python implementation")
    import pyblockify as bl

def get_blocklist_name(fid, vid):
    blpath = os.path.join(config.LISTS_DIR, "{}-{}".format(fid, version_id))

def get_file_info(fid):
    with db.connect() as c:
        row = c.execute('SELECT * FROM Files WHERE fid = ?', (fid,)).fetchone()
        if row is None:
            return None

        rows = c.execute('SELECT * FROM FileVersions WHERE fid = ?', (fid,)).fetchall()
        return [(r['vid'], r['dt_urc'], r['blocklist']) for r in rows]

def store_block(c, bdata):
    bhash = hashlib.sha256(bdata)
    bfname = "{}-{}.dat".format(bhash.hexdigest(), len(bdata))
    bfpath = os.path.join(config.BLOCKS_DIR, bfname)

    if os.path.exists(bfpath):
        #print("Hash conflict detected? {}".format(bfname))
        return bhash.digest()# TODO: already stored?
            
    with open(bfpath, 'wb') as f:
        f.write(bdata)
    c.execute('INSERT INTO Blocks VALUES (?,?,?)',
            (bhash.digest(), len(bdata), shared.sd.node.name))

    return bhash.digest()

def store_file_ext(sd, fspath, version_id=None):
    if version_id is None:
        version_id = uuid.uuid4().int % 2**32

    #fsize = os.path.getsize(fspath) # TODO: 16MB macroblocks
    if not os.path.exists(fspath):
        return None

    with db.connect() as c, open(fspath, 'rb') as f:
        fid = c.execute('INSERT INTO Files VALUES (NULL,?,?)',
                    (os.path.basename(fspath), sd.node.name)) \
                            .lastrowid
        blpath = get_blocklist_name(fid, version_id)

        # Get blocklist
        print("Reading file {}".format(fspath))
        blocklist = bl.blocklist(fspath)
        if blocklist is None:
            print("Error reading blocklist")
            return None

        # Save blocks
        print("Saving blocks")

        block_sizes = [blocklist[0]] + [blocklist[i]-blocklist[i-1] for i in range(1,len(blocklist))]
        with open(blpath, 'wb') as blf:
            for i,b in enumerate(blocklist):
                bsize = block_sizes[i]
                print("Block {}, size {}".format(b, bsize))

                bdata = f.read(bsize)
                if len(bdata) < bsize:
                    print("ERROR: block size wrong")
                    return None

                bhash = store_block(sd, c, bdata)
                blf.write(struct.pack("=L", len(bdata)))
                blf.write(bhash)

        # Enter version into DB
        dt_utc = int(time.mktime(time.gmtime()))
        c.execute('INSERT INTO FileVersions VALUES (?,?,?,?)',
                    (version_id, fid, dt_utc, blpath))

    sd.local.conn.commit()
    return fid

