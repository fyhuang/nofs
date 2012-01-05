#ifndef H_MEMSTREAM
#define H_MEMSTREAM

#include <arpa/inet.h>

#ifndef __APPLE__
#include <endian.h>
#else
#include <libkern/OSByteOrder.h>
#endif

#include <exception>

class end_of_stream : std::exception {
public:
    const char *what() { return "Reached end of memory stream"; }
};

template <bool net_transform>
class mem_stream {
private:
    const uint8_t *mBuffer;
    size_t mSize;
    size_t mPos;

public:
    mem_stream(const uint8_t *buf, size_t size) {
        reset(buf, size);
    }
    mem_stream(const std::vector<uint8_t> &vec) {
    	reset(&vec[0], vec.size());
    }

    void reset(const uint8_t *buf, size_t size) {
        mBuffer = buf;
        mSize = size;
        mPos = 0;
    }

    uint8_t read1() {
        if (mPos >= mSize) throw end_of_stream();
        return mBuffer[mPos++];
    }

    uint16_t read2() {
        if (mPos >= mSize-1) throw end_of_stream();
        uint16_t val = *((uint16_t*)(mBuffer + mPos));
        mPos += 2;
        if (net_transform) {
            return htons(val);
        }
        return val;
    }

    uint32_t read4() {
        if (mPos >= mSize-3) throw end_of_stream();
        uint32_t val = *((uint32_t*)(mBuffer + mPos));
        mPos += 4;
        if (net_transform) {
            return htonl(val);
        }
        return val;
    }

    uint64_t read8() {
        if (mPos >= mSize-7) throw end_of_stream();
        uint64_t val = *((uint64_t*)(mBuffer + mPos));
        mPos += 8;
        if (net_transform) {
#ifndef __APPLE__
            return betoh64(val);
#else
            return OSSwapBigToHostInt64(val);
#endif
        }
        return val;
    }

    void readBytesInto(uint8_t *destbuf, size_t nb) {
        if (mPos >= mSize-nb+1) throw end_of_stream(); 
        memcpy(destbuf, mBuffer+mPos, nb);
        mPos += nb;
    }
};

#endif
