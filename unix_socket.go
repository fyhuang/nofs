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
func ServeUnix(socket_filename string, quit chan int) {
    unix_addr, err := net.ResolveUnixAddr("unixgram", socket_filename)
    if err != nil {
        log.Fatal("net.ResolveUnixAddr:", err)
    }

    listener, err := net.ListenUnix("unix", unix_addr)
    if err != nil {
        log.Fatal("net.ListenUnix:", err)
    }
    defer listener.Close()
    defer os.Remove(socket_filename)

    log.Printf("Unix sockets listening...\n")

    for {
        conn, err := listener.AcceptUnix()
        if err != nil {
            log.Printf("Unable to accept: %v", err)
            continue
        }

        go unixHandleConn(conn)
    }

    quit <- 1
}

func unixHandleConn(c *net.UnixConn) {
    // JSON parsing flags
    bracketLevel := 0 // 0 = outside any JSON object; 1 = first level brackets; ...
    inJSON := false
    //inString := false

    buffer := make([]byte, BUFFER_LENGTH)
    ring := NewByteRing(BUFFER_LENGTH)
    for {
        n, err := c.Read(buffer)
        if err != nil {
            log.Fatal("net.UnixConn.Read:", err)
        }

        // TODO: handle strings
        for i := 0; i < n; i++ {
            if inJSON {
                ring.Write(buffer[i:i+1])
                if buffer[i] == '{' {
                    bracketLevel++
                }
                if buffer[i] == '}' {
                    bracketLevel--
                }

                if bracketLevel == 0 {
                    inJSON = false
                    json_bytes := ring.Slice()
                    log.Printf("Got packet: %v, %v\n", json_bytes, string(json_bytes))
                    unixHandleRequest(c, json_bytes)
                }
            } else {
                if buffer[i] == '{' {
                    inJSON = true
                    bracketLevel++
                    ring.Write(buffer[i:i+1])
                }
            }
        }
    }
}

func unixHandleRequest(c *net.UnixConn, json_bytes []byte) {
    // First check what kind of action it is
    var reqbase RequestBase
    err := json.Unmarshal(json_bytes, &reqbase)
    if err != nil {
        log.Printf("Packet doesn't look like a NoFS request: %v\n", string(json_bytes))
        return
    }

    time.Sleep(0.5e8)
    log.Printf("Unix request: %v\n", reqbase.Action)

    switch reqbase.Action {
    case "read":
        var fr FileRequest
        err = json.Unmarshal(json_bytes, &fr)
        if err != nil {
            log.Printf("Couldn't unmarshal packet: %v\n", json_bytes)
            return
        }

        read_response, _ := DoReadAction(&fr)
        json_buffer, _ := json.Marshal(read_response)
        c.Write(json_buffer)
    case "stat":
        var fr FileRequest
        err = json.Unmarshal(json_bytes, &fr)
        if err != nil {
            log.Printf("Couldn't unmarshal packet: %v\n", json_bytes)
            return
        }

        stat_response, _ := DoStatAction(&fr)
        json_buffer, _ := json.Marshal(stat_response)
        c.Write(json_buffer)
    case "index":
        var ir IndexRequest
        err = json.Unmarshal(json_bytes, &ir)
        if err != nil {
            log.Printf("Couldn't unmarshal packet: %v\n", json_bytes)
            return
        }

        index_response, _ := DoIndexAction(&ir)
        json_buffer, _ := json.Marshal(index_response)
        c.Write(json_buffer)
    default:
        log.Printf("Action %v unknown\n", reqbase.Action)
    }

    log.Printf("Packet sent\n")
}
