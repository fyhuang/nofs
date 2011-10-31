#ifndef H_NOFS_APPENDBUFFER
#define H_NOFS_APPENDBUFFER

/// A buffer which can be appended to
class AppendBuffer
{
private:
    uint8_t *mBuffer;
    /// Size of the buffer
    unsigned int mCapacity;
    /// How many bytes are currently stored in the buffer
    unsigned int mCount;

public:
    AppendBuffer(unsigned int capacity)
        : mBuffer(NULL), mCapacity(capacity), mCount(0)
    {
        mBuffer = new uint8_t[capacity];
    }

    ~AppendBuffer()
    {
        delete[] mBuffer;
    }

    void append(uint8_t byte)
    {
        // TODO: ability to resize buffer
        mBuffer[mCount] = byte;
        mCount++;

        // We want to be able to store a NULL byte
        // at the end
        assert(mCount < mCapacity);
    }

    // void clear()

    const char *toString()
    {
        mBuffer[mCount] = '\0';
        return mBuffer;
    }
};

#endif
