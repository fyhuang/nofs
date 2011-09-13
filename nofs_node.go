// NoFS node daemon
package main

import (
    "flag"
    "log"
    "syscall"
    //"os/signal"
    )

func main() {
    log.Printf("Starting NoFS node...\n")
    log.Printf("OS: %v\n", syscall.OS)
    // TODO: check OS
    // if syscall.OS != "windows" {
    // TODO: signal handling
    // }

    httpaddr := flag.String("httpaddr", ":4096", "address to listen on (HTTP server)")
    flag.Parse()

    quit_chan := make(chan int)
    go ServeHttp(*httpaddr, quit_chan)
    go ServeUnix("/tmp/nofs.socket", quit_chan)

    <-quit_chan
    <-quit_chan
}
