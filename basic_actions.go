package main

import (
    "os"
    "path"
    "io/ioutil"
    )

// Handlers for basic actions (read, stat, ...)
func DoReadAction(fr *FileRequest) (*ReadResponse, os.Error) {
    if len(fr.Bundle) == 0 {
        return &ReadResponse{"Failed;no bundle", nil}, os.NewError("No bundle")
    }

    if len(fr.Filename) == 0 {
        return &ReadResponse{"Failed;no filename", nil}, os.NewError("No filename")
    }

    // Open the file
    bundle := path.Join("files", fr.Bundle)
    file, err := os.Open(path.Join(bundle, fr.Filename))
    if err != nil {
        return &ReadResponse{"Failed;couldn't find/open file", nil}, os.NewError("Couldn't find/open file")
    }
    defer file.Close()

    bytes, err := ioutil.ReadAll(file)
    if err != nil {
        return &ReadResponse{"Failed;couldn't read file", nil}, os.NewError("Couldn't read file")
    }

    return &ReadResponse{"Success", bytes}, nil
}

func DoStatAction(fr *FileRequest) (*StatResponse, os.Error) {
    if len(fr.Bundle) == 0 {
        return &StatResponse{"Failed;no bundle", 1, ""}, os.NewError("No bundle")
    }

    bundle := path.Join("files", fr.Bundle)
    if len(fr.Filename) == 0 {
        // Looking for bundle stat
        fi, err := os.Stat(bundle)
        if err != nil {
            return &StatResponse{"Failed;bundle doesn't exist", 2, ""}, os.NewError("Bundle doesn't exist")
        }

        if !fi.IsDirectory() {
            return &StatResponse{"Failed;bundle not a directory", 2, ""}, nil
        }

        return &StatResponse{"Success", 0, "Bundle"}, nil
    } else {
        // Looking for file/dir stat
        fi, err := os.Stat(path.Join(bundle, fr.Filename))
        if err != nil {
            return &StatResponse{"Failed;file doesn't exist", 3, ""}, nil
        }

        if fi.IsDirectory() {
            return &StatResponse{"Success", 0, "Directory"}, nil
        } else {
            return &StatResponse{"Success", 0, "File"}, nil
        }
    }

    return nil, nil
}

func DoIndexAction(ir *IndexRequest) (*IndexResponse, os.Error) {
    return nil, nil
}
