#include <boost/circular_buffer.hpp>

#include <cstdio>
#include <cstdlib>
#include <stdint.h>

#define CDECL __attribute__((cdecl))

uint32_t ipow(uint32_t base, uint32_t exp) {
    uint32_t accum = 1;
    for (uint32_t i = 0; i < exp; i++) {
        accum *= base;
    }
    return accum;
}

struct BlockifyTask {
    const static int prime = 139;
    const static int window_size = 31;
    const static int block_size = 16*1024;
    const static long int __limit = 32*1024*1024;
    const static long int block_indicator = block_size - 1;

    int fd;
    uint64_t last_pos;
    bool done;

    boost::circular_buffer<uint8_t> window;
    uint32_t prime_pow;
    uint32_t csum;

    const static int buffer_size = 4096;
    uint8_t *buffer;
    int num_bytes_left;

    BlockifyTask(int fd)
        : window(window_size) {
        this->fd = fd;
        last_pos = 0;
        done = false;

        for (int i = 0; i < window_size; i++) {
            window.push_back(0);
        }

        prime_pow = ipow(prime, window_size);
        csum = 1;

        buffer = new uint8_t[buffer_size];
        num_bytes_left = 0;
    }

    int nextByte() {
        if (num_bytes_left == 0) {
            ssize_t size = read(fd, buffer, buffer_size);
            if (size <= 0) return EOF;
            num_bytes_left = size;
        }

        return buffer[buffer_size - (num_bytes_left--)];
    }
};


extern "C" {

BlockifyTask *beginBlockify(int fd) {
    BlockifyTask *bt = new BlockifyTask(fd);
    return bt;
}

uint64_t nextBlock(BlockifyTask *bt) {
    if (bt->done) {
        return 0;
    } else {
        while (true) {
            int c = bt->nextByte();
            if (c == EOF) break;

            bt->last_pos++;
            if (bt->last_pos % (1024*1024) == 0) {
                printf("Read %lld MB\n", bt->last_pos / (1024*1024));
            }

            uint8_t pc = bt->window.front();
            bt->window.pop_front();
            bt->window.push_back(c);

            bt->csum *= bt->prime;
            bt->csum += c;
            bt->csum -= pc * bt->prime_pow;
            
            if (bt->csum % bt->block_size == bt->block_indicator) {
                //printf("Block at %lld\n", bt->last_pos);
                return bt->last_pos;
            }
        }

        bt->done = true;
        return bt->last_pos+1;
    }
}

void endBlockify(BlockifyTask *bt) {
    delete bt;
}

}
