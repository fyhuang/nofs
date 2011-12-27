#ifndef H_MEMSTREAM
#define H_MEMSTREAM

#include <arpa/inet.h>
#include <exception>

class end_of_stream : std::exception {
};

template <bool do_net_transform>
class mem_stream {
private:
    uint8_t *mBuffer;
    size_t mSize;
    size_t mPos;

public:
    mem_stream(uint8_t *buf, size_t size) {
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
        if (do_net_transform) {
            return htons(val);
        }
        return val;
    }

    uint16_t read4() {
        if (mPos >= mSize-3) throw end_of_stream();
        uint32_t val = *((uint32_t*)(mBuffer + mPos));
        mPos += 4;
        if (do_net_transform) {
            return htonl(val);
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
