package main

import (
    "os"
    "path"
    "io/ioutil"
    )

import . "./nofs"

const filesDir = "files"

// Handlers for basic actions (read, stat, ...)
func DoReadAction(fr *FileRequest) (*ReadResponse, os.Error) {
    if len(fr.Bundle) == 0 {
        return &ReadResponse{"Failed;no bundle", nil}, os.NewError("No bundle")
    }

    if len(fr.Filename) == 0 {
        return &ReadResponse{"Failed;no filename", nil}, os.NewError("No filename")
    }

    // Open the file
    bundle := path.Join(filesDir, fr.Bundle)
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
        return &StatResponse{"Failed;no bundle", 1, "", 0}, os.NewError("No bundle")
    }

    bundle := path.Join(filesDir, fr.Bundle)
    if len(fr.Filename) == 0 {
        // Looking for bundle stat
        fi, err := os.Stat(bundle)
        if err != nil {
            return &StatResponse{"Failed;bundle doesn't exist", 2, "", 0}, os.NewError("Bundle doesn't exist")
        }

        if !fi.IsDirectory() {
            return &StatResponse{"Failed;bundle not a directory", 2, "", 0}, nil
        }

        return &StatResponse{"Success", 0, "Bundle", 0}, nil
    } else {
        // Looking for file/dir stat
        fi, err := os.Stat(path.Join(bundle, fr.Filename))
        if err != nil {
            return &StatResponse{"Failed;file doesn't exist", 3, "", 0}, nil
        }

        if fi.IsDirectory() {
            return &StatResponse{"Success", 0, "Directory", 0}, nil
        } else {
            return &StatResponse{"Success", 0, "File", fi.Size}, nil
        }
    }

    return nil, nil
}

func DoIndexAction(ir *IndexRequest) (*IndexResponse, os.Error) {
	var rootPath string
	if len(ir.Bundle) == 0 {
		rootPath = filesDir
	} else if len(ir.Path) == 0 {
		fullPath := path.Join(filesDir, ir.Bundle)
		fi, err := os.Stat(fullPath)
		if err != nil || !fi.IsDirectory() {
			return &IndexResponse{"Failed;bundle doesn't exist", ir.RequestId, 2, nil}, nil
		}
		rootPath = fullPath
	} else {
		bundlePath := path.Join(filesDir, ir.Bundle)
		fullPath := path.Join(bundlePath, ir.Path)
		fi, err := os.Stat(fullPath)
		if err != nil || !fi.IsDirectory() {
			return &IndexResponse{"Failed;directory doesn't exist", ir.RequestId, 3, nil}, nil
		}
		rootPath = fullPath
	}

	// Read the files in directory
	entries, err := ioutil.ReadDir(rootPath)
	if err != nil {
		return &IndexResponse{"Failed;couldn't read directory", ir.RequestId, 4, nil}, nil
	}
	index := []IndexEntry{}
	for _, entry := range entries {
		index = append(index, IndexEntry{entry.Name, entry.IsDirectory()})
	}

	return &IndexResponse{"Success", ir.RequestId, 0, index}, nil
}
