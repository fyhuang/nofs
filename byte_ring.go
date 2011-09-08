package main

import (
    "os"
    )

// Ring buffer for bytes
type ByteRing struct {
    buffer []byte
    readPos int
    writePos int
}

// Returns a new byte ring with size n
func NewByteRing(n int) (*ByteRing) {
    return &ByteRing{make([]byte, n), 0, 0}
}

// How many bytes are ready to be read
func (br *ByteRing) Count() int {
    wp := br.writePos
    if wp < br.readPos {
        wp += len(br.buffer)
    }
    return wp - br.readPos
}

// How much space is left in the buffer
func (br *ByteRing) BytesLeft() int {
    rp := br.readPos
    if rp < br.writePos {
        rp += len(br.buffer)
    } else if rp == br.writePos {
        return len(br.buffer) - 1
    }
    return rp - br.writePos - 1
}

func (br *ByteRing) Read(into []byte) (int, os.Error) {
    bytesToCopy := len(into)
    // Some error checking on readPos
    count := br.Count()
    if count == 0 {
        return 0, os.NewError("Nothing to read in buffer")
    }
    if bytesToCopy > count {
        bytesToCopy = count
    }

    copy(into, br.buffer[br.readPos:br.readPos+bytesToCopy])
    br.readPos += bytesToCopy
    br.readPos = br.readPos % len(br.buffer)

    return bytesToCopy, nil
}

func (br *ByteRing) Slice() ([]byte) {
    result := make([]byte, br.Count())
    br.Read(result)
    return result
}

func (br *ByteRing) Write(from []byte) (int, os.Error) {
    bytesToCopy := len(from)
    // Some error checking on readPos
    count := br.BytesLeft()
    if count == 0 {
        return 0, os.NewError("Buffer is full")
    }
    if bytesToCopy > count {
        bytesToCopy = count
    }

    copy(br.buffer[br.writePos:br.writePos+bytesToCopy], from)
    br.writePos += bytesToCopy
    br.writePos = br.writePos % len(br.buffer)

    return bytesToCopy, nil
}
