package nofs

import (
	"net"
	)

// Types for requests, responses
type RequestBase struct {
    Action string
}

type FileRequest struct {
    Action string
    Bundle string
    Filename string
    Data64 string
}

type IndexRequest struct {
    Action string
    SimpleOutput bool
    Bundle string
    Path string
}



type ReadResponse struct {
    Result string
    Data64 []byte
}

type StatResponse struct {
    Result string
    ResultCode int
    FileType string
	FileSize int64
}

type IndexResponse struct {
    Result string
    ResultCode int
}

// Read a full JSON object from the connection
func ReadJson(conn net.Conn) (result []byte) {
	buffer := bufferMap[conn]
	if buffer == nil {
		bufferMap[conn] = NewStatefulBuffer(4096)
		buffer = bufferMap[conn]
	}

	bracketLevel := 0
	inJson := false
	//inString := false

	ab := NewAppendBuffer(4096)
	result = nil
	for result == nil {
		for ; !buffer.AtEnd(); buffer.ReadPos++ {
			i := buffer.ReadPos
			if inJson {
				rb := buffer.Buffer[i]
				ab.Append(rb)
				if rb == '{' {
					bracketLevel++
				} else if rb == '}' {
					bracketLevel--
				}

				if bracketLevel == 0 {
					inJson = false
					result = ab.Bytes()
					break
				}
			} else {
				if buffer.Buffer[i] == '{' {
					inJson = true
					bracketLevel++
					ab.Append('{')
				}
			}
		}
	}

	return result
}

var bufferMap map[net.Conn]*StatefulBuffer
