package main

import (
    "os"
    "net"
    "json"
    "log"
    "time"
    )

const BUFFER_LENGTH = 1024 * 128

// Unix socket handling for Node server
func ServeUnix(addr string, quit chan int) {
    unix_addr, err := net.ResolveUnixAddr("unixgram", addr)
    if err != nil {
        log.Fatal("net.ResolveUnixAddr:", err)
    }

    conn, err := net.ListenUnixgram("unixgram", unix_addr)
    if err != nil {
        log.Fatal("net.ListenUnixgram:", err)
    }
    defer conn.Close()
    defer os.Remove(addr)

    log.Printf("Unix sockets listening...\n")

    bytes := make([]byte, BUFFER_LENGTH)
    for {
        n, addr, err := conn.ReadFrom(bytes)
        if err != nil {
            log.Fatal("net.PacketConn.ReadFrom:", err)
        }

        // Parse JSON
        var fr FileRequest
        err = json.Unmarshal(bytes[0:n], &fr)
        if err != nil {
            log.Printf("Couldn't unmarshal packet: %v\n", bytes[0:n])
            continue
        }

        time.Sleep(2e9)
        log.Printf("Unix request: %v\n", fr.Action)

        switch fr.Action {
        case "read":
            read_response, _ := DoReadAction(&fr);
            json_bytes, _ := json.Marshal(read_response)
            conn.WriteTo(json_bytes, addr)
            log.Printf("Unix wrote to socket\n")
        case "stat":
            DoStatAction(&fr);
        default:
            log.Printf("Action %v unknown\n", fr.Action)
        }
    }

    quit <- 1
}
