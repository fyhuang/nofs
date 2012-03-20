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
import sqlite3
import struct
from contextlib import closing

import config
try:
    import cblockify as bl
except ImportError:
    print("Warning: optimized blockify not found, using slow Python implementation")
    import pyblockify as bl


DB_SCHEMA = """
CREATE TABLE UserSettings (
    name VARCHAR(255) PRIMARY KEY,
    value VARCHAR(255)
    );

CREATE TABLE PeerNodes (
    name VARCHAR(255) PRIMARY KEY,
    last_hostname VARCHAR(255),
    last_ip VARCHAR(255)
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

def get_file_info(fid):
    with closing(sd.local.conn.cursor()) as c:
        c.execute('SELECT * FROM Files WHERE fid = ?', (fid,))
        row = c.fetchone()
        if row is None:
            return None

        c.execute('SELECT * FROM FileVersions WHERE fid = ?', (fid,))
        rows = c.fetchall()
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
            (bhash.digest(), len(bdata), sd.node.name))

    return bhash.digest()

def store_file_ext(sd, fspath, version_id=None):
    if version_id is None:
        version_id = uuid.uuid4().int % 2**32

    #fsize = os.path.getsize(fspath) # TODO: 16MB macroblocks
    if not os.path.exists(fspath):
        return None

    with closing(sd.local.conn.cursor()) as c, open(fspath, 'rb') as f:
        c.execute('INSERT INTO Files VALUES (NULL,?,?)',
                    (os.path.basename(fspath), sd.node.name))
        fid = c.lastrowid
        blpath = os.path.join(config.LISTS_DIR, "{}-{}".format(fid, version_id))

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

