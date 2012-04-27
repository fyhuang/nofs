import sqlite3
import threading
from contextlib import closing

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

CREATE TABLE Directories (
    dirid INTEGER PRIMARY KEY,
    dirpath NVARCHAR(255)
    );

CREATE TABLE Files (
    fid INTEGER PRIMARY KEY,
    filename NVARCHAR(255),
    owner VARCHAR(255),
    dirid INTEGER,

    FOREIGN KEY(dirid) REFERENCES Directories(dirid)
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

_local = threading.local()

def connect():
    if 'dbconn' not in _local:
        _local.dbconn = sqlite3.connect(config.DB_FILE)
        c = _local.dbconn.cursor()

        tables_created = True
        try:
            c.execute('SELECT COUNT(*) FROM UserSettings')
        except sqlite3.OperationalError:
            tables_created = False

        if not tables_created:
            # Create the DB tables
            c.executescript(DB_SCHEMA)
            # TODO: ask user for initial settings
            _local.dbconn.commit()
        c.close()

    return _local.dbconn
