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
func GetStatResponse(conn *net.UnixConn, data []byte) (*nofs.StatResponse) {
	conn.Write(data)
	result := nofs.ReadJson(conn)
	resp := &nofs.StatResponse{}
	err := json.Unmarshal(result, resp)
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
		json_bytes, err := json.Marshal(&nofs.FileRequest{"stat", bundle, path, ""})
		if err != nil {
			slog.Printf("Couldn't marshal packet: %v\n", err)
			return nil, fuse.EIO
		}
		resp := GetStatResponse(this.conn, json_bytes)

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

func (this *NoFSFuse) OpenDir(rawpath string, context *fuse.Context) (c chan fuse.DirEntry, code fuse.Status) {
	if rawpath == "" {
		c = make(chan fuse.DirEntry)
		c <- fuse.DirEntry{Name: "inbox", Mode: fuse.S_IFDIR}
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
		log.Fatal("Couldn't resolve address: %v\n", err)
	}

	conn, err := net.DialUnix("unix", nil, addr)
	if err != nil {
		log.Fatal("Couldn't connect to NoFS node: %v\n", err)
	}
	defer conn.Close()

	state, _, err := fuse.MountPathFileSystem(flag.Arg(0), &NoFSFuse{conn: conn}, nil)
	if err != nil {
		log.Fatal("Mount failure: %v\n", err)
	}

	state.Loop(false) // TODO: not threaded for now
}
