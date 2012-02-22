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
import sqlite3
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
    length INTEGER
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

def store_file(sd, fspath, version_id=None):
    if version_id is None:
        version_id = uuid.uuid4().int

    fsize = os.path.getsize(fspath) # TODO: 16MB macroblocks

    print("Reading file {}".format(fspath))
    with open(fspath, 'rb') as f:
        blocklist = bl.blocklist(f, int(1*1024*1024))
    dt_utc = int(time.mktime(time.gmtime()))

    # Save blocks
    print("Saving blocks")
    for b in blocklist:
        print(b)

    # Enter into DB
    with closing(sd.local.conn.cursor()) as c:
        c.execute('INSERT INTO Files VALUES (NULL,?,?)',
                    (fspath, sd.node.name))
        fid = c.lastrowid
        c.execute('INSERT INTO FileVersions VALUES (?,?,?,?)',
                    (version_id, fid, dt_utc, blpath))

    version = VersionData(version_id, dt_utc, blocklist)

    fid = uuid.uuid4().bytes
    fe = FileEntry(fid, 'blocks')
    fe.versions[version_id] = version

    # Add file to index
    print("Adding file {} to index".format(fid))
    with sd.storage_lock:
        sd.file_index[fid] = fe
