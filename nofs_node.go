// NoFS node daemon
package main

import (
    "flag"
    )

func main() {
    httpaddr := flag.String("httpaddr", ":4096", "address to listen on (HTTP server)")
    flag.Parse()

    quit_chan := make(chan int)
    go ServeHttp(*httpaddr, quit_chan)
    go ServeUnix("/tmp/nofs.socket", quit_chan)

    <-quit_chan
    <-quit_chan
}

type FileRequest struct {
    Action string
    Bundle string
    Filename string
    Data64 string
}

type ReadResponse struct {
    Result string
    Data64 []byte
}

type StatResponse struct {
    Result string
    FileType string
    //ACL []Permission
}
