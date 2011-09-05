// NoFS node daemon
package main

import (
    "flag"
    "fmt"
    "path"
    "http"
    "log"
    "strings"
    "io"
    "io/ioutil"
    "json"
    "os"
    )

func main() {
    addr := flag.String("addr", ":4096", "address to listen on")
    flag.Parse()

    http.Handle("/", http.HandlerFunc(ReqHandler))
    fmt.Println("Listening...")
    err := http.ListenAndServe(*addr, nil)
    if err != nil {
        log.Fatal("http.ListenAndServe:", err)
    }

    /*fmt.Printf("Accepting connection...\n")

    addr, _ := net.ResolveTCPAddr("tcp", "127.0.0.1:4096")
    l, _ := net.ListenTCP("tcp", addr)
    conn, _ := l.AcceptTCP()

    reader := bufio.NewReader(conn)
    line, _, _ := reader.ReadLine()
    fmt.Printf("Got line %v", line)

    conn.Close()*/
}

type FileRequest struct {
    Action string
    Bundle string
    Filename string
    Data64 string
}

type FileResponse struct {
    Result string
    Data64 string
}

func ReqHandler(w http.ResponseWriter, req *http.Request) {
    log.Printf("Received request (%v): %v\n",
               req.Method, req.URL.Path);

    var json_stream io.Reader
    switch req.Method {
    case "GET":
        fv := req.FormValue("q")
        if len(fv) == 0 {
            // Serve files
            ServeFiles(w, req)
            return
        }
        json_stream = strings.NewReader(fv)
    case "POST":
        json_stream = req.Body
    default:
        log.Printf("Method %v not supported\n", req.Method)
    }

    var fr FileRequest
    json_bytes, err := ioutil.ReadAll(json_stream)
    if err != nil { return }
    err = json.Unmarshal(json_bytes, &fr)
    if err != nil { return }

    out_str := fmt.Sprintf("Requested %v\n", fr.Action)
    w.Write([]byte(out_str))
}

func ServeFiles(w http.ResponseWriter, req *http.Request) {
    filename := req.URL.Path
    if filename[len(filename)-1] == '/' {
        filename += "index.html"
    }

    log.Printf("Serving file %v\n", filename)
    file, err := os.Open(path.Join("media", filename))
    if err != nil {
        w.WriteHeader(http.StatusNotFound)
        return
    }
    defer file.Close()

    bytes, err := ioutil.ReadAll(file)
    if err != nil {
        w.WriteHeader(http.StatusInternalServerError)
        return
    }
    w.Write(bytes)
}
