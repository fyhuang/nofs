#include <sys/socket.h>

#include <vector>

/** A class to read stuff from a socket */
class SocketReader {
private:
    int mSocket;

    std::vector<uint8_t> mBuffer;
    int mBufferPos;

public:
    SocketReader(int s)
        : mSocket(s), mBuffer(), mBufferPos(0)
    {
    }

    void readMoreBytes()
    {
        if (mBufferPos >= mBuffer.size()) {
            mBuffer.clear();
            mBuffer.resize(BUFFER_LENGTH);
            int count = recv(s, &mBuffer[0], BUFFER_LENGTH);
            if (count < 0) {
                perror("nofs: recv");
                return NULL;
            }
            mBuffer.resize(count);

            mBufferPos = 0;
        }
    }

    AppendBuffer *nextJSON()
    {
        int bracket_level = 0;
        bool in_json = false;
        // TODO bool in_string = false;

        AppendBuffer *result = new AppendBuffer(BUFFER_LENGTH);
        bool found = false;
        while (!found) {
            readMoreBytes();

            for (; mBufferPos < mBuffer.size(); mBufferPos++) {
                int i = mBufferPos;
                if (in_json) {
                    uint8_t byte = mBuffer[i];
                    result->append(byte);
                    if (byte == '{') {
                        bracket_level++;
                    }
                    else if (byte == '}') {
                        bracket_level--;
                    }

                    if (bracket_level == 0) {
                        in_json = false;
                        found = true;
                        break;
                    }
                }
                else {
                    if (mBuffer[i] == '{') {
                        in_json = true;
                        bracket_level++;
                        result->append('{');
                    }
                }
            }
        }

        return result;
    }
};
