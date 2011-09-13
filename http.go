package main

import (
    "http"
    "log"
    "os"
    "path"
    "io"
    "io/ioutil"
    "strings"
    "json"
	"./nofs"
    )

// HTTP protocol handling for Node server
func ServeHttp(addr string, quit chan int) {
    http.Handle("/", http.HandlerFunc(httpReqHandler))
    log.Printf("HTTP listening on %v...\n", addr)
    err := http.ListenAndServe(addr, nil)
    if err != nil {
        log.Fatal("http.ListenAndServe:", err)
    }
    quit <- 1
}

func httpServeFiles(w http.ResponseWriter, req *http.Request) {
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

func httpReqHandler(w http.ResponseWriter, req *http.Request) {
    log.Printf("Received request (%v): %v\n",
               req.Method, req.URL.Path);

    var json_stream io.Reader
    switch req.Method {
    case "GET":
        fv := req.FormValue("q")
        if len(fv) == 0 {
            // Serve files
            httpServeFiles(w, req)
            return
        }
        json_stream = strings.NewReader(fv)
    case "POST":
        json_stream = req.Body
    default:
        log.Printf("Method %v not supported\n", req.Method)
    }

    var fr nofs.FileRequest
    json_bytes, err := ioutil.ReadAll(json_stream)
    if err != nil { return }
    err = json.Unmarshal(json_bytes, &fr)
    if err != nil { return }

    switch fr.Action {
    case "read":
        read_response, _ := DoReadAction(&fr);
        json_bytes, _ := json.Marshal(read_response)
        w.Write(json_bytes)
    case "stat":
        DoStatAction(&fr);
    default:
        log.Printf("Action %v unknown\n", fr.Action)
    }
}
