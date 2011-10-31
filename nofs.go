package nofs

import (
	"net"
	"os"
	)

// Types for requests, responses
type RequestBase struct {
    Action string

	/* This field is optional. If you are communicating
	 * asynchronously with the node, you can use this field
	 * to keep track of request/response pairs.
	 */
	RequestId int
}

type FileRequest struct {
    Action string
	RequestId int

    Bundle string
    Filename string
    Data64 string
}

type IndexRequest struct {
    Action string
	RequestId int

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

// An entry in the index
type IndexEntry struct {
	Name string
	Directory bool
}

type IndexResponse struct {
    Result string
	RequestId int

    ResultCode int
	Index []IndexEntry
}


// Encapsulates state needed to read JSON from a connection
type JsonReader struct {
	conn net.Conn
	buffer *StatefulBuffer
}

func NewJsonReader(conn net.Conn) (*JsonReader) {
	return &JsonReader{conn, NewStatefulBuffer(4096)}
}

// Read a full JSON object from the connection
func (this *JsonReader) ReadJson() (result []byte, err os.Error) {
	buffer := this.buffer

	bracketLevel := 0
	inJson := false
	//inString := false

	ab := NewAppendBuffer(4096)
	result = nil
	for result == nil {
		if buffer.AtEnd() {
			buffer.Reset()
			n, err := this.conn.Read(buffer.Buffer)
			if err != nil {
				return nil, err
			} else if n == 0 {
				return nil, nil // TODO: closed connection
			}
		}

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

	return result, nil
}

