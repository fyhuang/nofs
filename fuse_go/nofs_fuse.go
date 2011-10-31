package main

// FUSE client in Go
import (
	"os"
	"net"
	"github.com/fyhuang/go-fuse/fuse"
	"syslog"
	"strings"
	"flag"
	"log"
	"../nofs"
	"json"
	)

var slog = syslog.NewLogger(syslog.LOG_ERR, 0)

type NoFSFuse struct {
	conn *net.UnixConn
	reader *nofs.JsonReader

	fuse.DefaultFileSystem
}

func SplitPath(rawpath string) (bundle string, path string) {
	index := strings.Index(rawpath, "/")
	if index == -1 || index == len(rawpath) - 1 {
		return rawpath, ""
	}
	return rawpath[0:index], rawpath[index+1:]
}

// Warning: this blocks until a response is received
func (fs *NoFSFuse) GetStatResponse(data []byte) (*nofs.StatResponse) {
	fs.conn.Write(data)
	result, err := fs.reader.ReadJson()
	resp := &nofs.StatResponse{}
	err = json.Unmarshal(result, resp)
	if err != nil {
		slog.Printf("Couldn't unmarshal packet %v: %v\n", string(result), err)
		return nil
	}
	return resp
}

func (fs *NoFSFuse) GetIndexResponse(data []byte) (*nofs.IndexResponse) {
	fs.conn.Write(data)
	result, err := fs.reader.ReadJson()
	resp := &nofs.IndexResponse{}
	err = json.Unmarshal(result, resp)
	if err != nil {
		slog.Printf("Couldn't unmarshal packet %v: %v\n", string(result), err)
		return nil
	}
	return resp
}


func (this *NoFSFuse) GetAttr(rawpath string, context *fuse.Context) (*os.FileInfo, fuse.Status) {
	slog.Printf("GetAttr %v", rawpath)
	if rawpath == "" {
		// Root directory
		return &os.FileInfo {
			Mode: fuse.S_IFDIR | 0755,
		}, fuse.OK
	} else {
		bundle, path := SplitPath(rawpath)
		json_bytes, err := json.Marshal(&nofs.FileRequest{"stat", 0, bundle, path, ""})
		if err != nil {
			slog.Printf("Couldn't marshal packet: %v\n", err)
			return nil, fuse.EIO
		}
		resp := this.GetStatResponse(json_bytes)

		if resp.ResultCode == 2 || resp.ResultCode == 3 {
			return nil, fuse.ENOENT
		} else if resp.ResultCode == 0 {
			if resp.FileType == "Bundle" || resp.FileType == "Directory" {
				return &os.FileInfo {
					Mode: fuse.S_IFDIR | 0555,
				}, fuse.OK
			} else {
				return &os.FileInfo {
					Mode: fuse.S_IFREG | 0444,
					Size: resp.FileSize,
				}, fuse.OK
			}
		} else {
			return nil, fuse.EIO
		}
	}

	return nil, fuse.EIO
}

// TODO: error checking
func (this *NoFSFuse) OpenDir(rawpath string, context *fuse.Context) (c chan fuse.DirEntry, code fuse.Status) {
	c = make(chan fuse.DirEntry)
	if rawpath == "" {
		json_bytes, _ := json.Marshal(&nofs.IndexRequest{"index", 0, true, "", ""})
		resp := this.GetIndexResponse(json_bytes)

		for _, entry := range resp.Index {
			c <- fuse.DirEntry{Name: entry.Name, Mode: fuse.S_IFDIR}
		}
		close(c)

		return c, fuse.OK
	} else {
		bundle, path := SplitPath(rawpath)
		json_bytes, _ := json.Marshal(&nofs.IndexRequest{"index", 0, true, bundle, path})
		resp := this.GetIndexResponse(json_bytes)
		if resp.ResultCode != 0 {
			return nil, fuse.ENOENT
		}

		for _, entry := range resp.Index {
			de := fuse.DirEntry{Name: entry.Name}
			if entry.Directory {
				de.Mode = fuse.S_IFDIR
			} else {
				de.Mode = fuse.S_IFREG
			}
			c <- de
		}
		close(c)

		return c, fuse.OK
	}

	return nil, fuse.ENOENT
}

func main() {
	flag.Parse()
	if len(flag.Args()) < 1 {
		log.Fatal("Usage:\n\tnofs_fuse MOUNTPOINT\n")
	}

	// Try to connect to node server
	addr, err := net.ResolveUnixAddr("unix", "/tmp/nofs.socket")
	if err != nil {
		log.Fatal("Couldn't resolve address: ", err)
	}

	conn, err := net.DialUnix("unix", nil, addr)
	if err != nil {
		log.Fatal("Couldn't connect to NoFS node: ", err)
	}
	defer conn.Close()
	log.Println("Connected to NoFS node!")

	fs := &NoFSFuse{
		conn: conn,
		reader: nofs.NewJsonReader(conn),
	}
	state, _, err := fuse.MountPathFileSystem(flag.Arg(0), fs, nil)
	if err != nil {
		log.Fatal("Mount failure: ", err)
	}

	state.Loop(false) // TODO: not threaded for now
}
