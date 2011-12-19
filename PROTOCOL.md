Client-to-node communication
=========

All packets look like:

    {
        "action": (ACTION),
        ["requestid": (REQUESTID),]
        
        // action-specific properties
    }

Where `(ACTION)` is one of:

* stat
* index
* stop

And `(REQUESTID)` is a client-specified integer, usually unique, which allows the client to differentiate between replies. The "requestid" field is optional.

File actions
========

File actions are stat, read, and write. They share a common structure:

{
    "action": "stat",
    "requestid": (REQUESTID),

    "bundle": (BUNDLE),
    "filepath": (FILEPATH),
    ["data64": (DATA64)]
}

Where `(BUNDLE)` is a string (with no path separators) that specifies the name of the bundle, `(FILEPATH)` is a string specifying the path to the file (starting with a forward slash), and `(DATA64)` is an optional field to pass other data in.

The stat action gets data about a file, directory, or bundle. It takes nothing in the data field. The "filepath" field is optional: if only a bundle name is provided, some information about that bundle will be returned.

The read action reads data from a file. It takes nothing in the data field. Both the bundle and filepath are required, and filepath must point to an actual file (not a directory).

The write action writes data into a file. TODO


Node-to-client responses
=============

Stat responses look like:

{
    "result": (RESULTSTRING),
    "resultcode": (RESULTCODE),
    "filetype": (FILETYPE),
    "filesize": (FILESIZE)
}

`(FILETYPE)` is one of "bundle", "directory", "file" (symlinks are not supported). `(FILESIZE)` is an integer, the number of bytes in the file.
