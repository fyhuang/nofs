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

import uuid
import hashlib
import sqlite3
import struct
from contextlib import closing

import config

DB_SCHEMA = """
CREATE TABLE UserSettings (
    name VARCHAR(255) PRIMARY KEY,
    value VARCHAR(255)
    );

CREATE TABLE Files (
    fid INTEGER PRIMARY KEY,
    filename NVARCHAR(255),
    owner VARCHAR(255)
    );

CREATE TABLE FileVersions (
    vid INTEGER,
    fid INTEGER,
    dt_utc INTEGER,
    -- TODO: metadata
    blocklist VARCHAR(255),
    FOREIGN KEY(fid) REFERENCES Files(fid)
    );

CREATE TABLE Blocks (
    hash CHAR(32),
    length INTEGER,
    owner VARCHAR(255)
    );
"""

def get_connection():
    conn = sqlite3.connect(config.DB_FILE)
    c = conn.cursor()

    tables_created = True
    try:
        c.execute('SELECT COUNT(*) FROM UserSettings')
    except sqlite3.OperationalError:
        tables_created = False

    if not tables_created:
        # Create the DB tables
        c.executescript(DB_SCHEMA)
        # TODO: ask user for initial settings

    conn.commit()
    c.close()
    return conn

import time
import os.path
try:
    import cblockify as bl
except ImportError:
    print("Warning: optimized blockify not found, using slow Python implementation")
    import pyblockify as bl

def store_block(c, bdata):
    bhash = hashlib.sha256(bdata)
    bfname = "{}-{}.dat".format(bhash.hexdigest(), len(bdata))
    bfpath = os.path.join(config.BLOCKS_DIR, bfname)
    if os.path.exists(bfpath):
        if os.path.getsize(bfpath) != len(bdata):
            print("Hash conflict detected? {}".format(bfname))
            return
            
    with open(bfpath, 'wb') as f:
        f.write(bdata)
    c.execute('INSERT INTO Blocks VALUES (?,?)', (bhash.digest(), len(bdata)))
    return bhash.digest()

def store_file(sd, fspath, version_id=None):
    if version_id is None:
        version_id = uuid.uuid4().int % 2**32

    fsize = os.path.getsize(fspath) # TODO: 16MB macroblocks

    with closing(sd.local.conn.cursor()) as c:
        c.execute('INSERT INTO Files VALUES (NULL,?,?)',
                    (fspath, sd.node.name))
        fid = c.lastrowid
        blpath = os.path.join(config.LISTS_DIR, "{}-{}".format(fid, version_id))

        print("Reading file {}".format(fspath))
        with open(fspath, 'rb') as f:
            blocklist = bl.blocklist(f)

            # Save blocks
            print("Saving blocks")

            f.seek(0)
            prev_block = 0
            with open(blpath, 'wb') as blf:
                for b in blocklist:
                    bsize = b - prev_block
                    print("Block {}, size {}".format(b, bsize))

                    bdata = f.read(bsize)
                    if len(bdata) < bsize:
                        print("ERROR: block size wrong")
                        break

                    bhash = store_block(c, bdata)
                    blf.write(struct.pack("=L", len(bdata)))
                    blf.write(bhash)

                    prev_block = b

        # Enter version into DB
        dt_utc = int(time.mktime(time.gmtime()))
        c.execute('INSERT INTO FileVersions VALUES (?,?,?,?)',
                    (version_id, fid, dt_utc, blpath))

    sd.local.conn.commit()
