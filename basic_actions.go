package main

import (
    "os"
    "path"
    "io/ioutil"
    )

// Handlers for basic actions (read, stat, ...)
func DoReadAction(fr *FileRequest) (*ReadResponse, os.Error) {
    if len(fr.Bundle) == 0 {
        return &ReadResponse{"Failed; no bundle", nil}, os.NewError("No bundle")
    }

    if len(fr.Filename) == 0 {
        return &ReadResponse{"Failed; no filename", nil}, os.NewError("No filename")
    }

    // Open the file
    bundle := path.Join("files", fr.Bundle)
    file, err := os.Open(path.Join(bundle, fr.Filename))
    if err != nil {
        return &ReadResponse{"Failed; couldn't find/open file", nil}, os.NewError("Couldn't find/open file")
    }
    defer file.Close()

    bytes, err := ioutil.ReadAll(file)
    if err != nil {
        return &ReadResponse{"Failed; couldn't read file", nil}, os.NewError("Couldn't read file")
    }

    return &ReadResponse{"Success", bytes}, nil
}

func DoStatAction(fr *FileRequest) {
    // TODO
    return
}
