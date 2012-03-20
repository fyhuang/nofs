#include <boost/circular_buffer.hpp>

#include <cstdio>
#include <cstdlib>
#include <stdint.h>

#define CDECL __attribute__((cdecl))

// Uses SHA-256 <http://www.aarongifford.com/computers/sha.html> to compute
// hash functions of blocks

// Uses Rabin fingerprints (e.g. http://gsoc.cat-v.org/people/mjl/blog/2007/08/06/1_Rabin_fingerprints/) for block boundaries

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

    FILE *fp;
    uint64_t last_pos;
    bool done;

    boost::circular_buffer<uint8_t> window;
    uint32_t prime_pow;
    uint32_t csum;

    const static int buffer_size = 4096;
    uint8_t *buffer;
    int num_bytes_left;

    BlockifyTask(FILE *fp)
        : window(window_size) {
        this->fp = fp;
        last_pos = 0;
        done = false;

        for (int i = 0; i < window_size; i++) {
            window.push_back(0);
        }

        prime_pow = ipow(prime, window_size);
        csum = 0;

        buffer = new uint8_t[buffer_size];
        num_bytes_left = 0;
    }

    int nextByte() {
        /*if (num_bytes_left == 0) {
            ssize_t size = read(fd, buffer, buffer_size);
            if (size <= 0) return EOF;
            num_bytes_left = size;
        }

        return buffer[buffer_size - (num_bytes_left--)];*/
        return fgetc(fp);
    }
};


extern "C" {

BlockifyTask *beginBlockify(const char *filename) {
    FILE *fp = fopen(filename, "rb");
    if (fp == NULL) return NULL;
    BlockifyTask *bt = new BlockifyTask(fp);
    printf("Successfully opened %s for reading\n", filename);
    return bt;
}

int nextBlock(BlockifyTask *bt, char *outbuf) {
    if (bt->done) {
        return -1;
    } else {
        //printf("Getting next block\n");
        // Block offset + SHA-256 + NULL byte (for Python)
        memset(outbuf, 0, 8+(256/8)); // TODO
        uint64_t *pos_ptr = (uint64_t *)(&outbuf[0]);

        while (true) {
            int c = bt->nextByte();
            if (c == EOF) break;

            bt->last_pos++;
            if (bt->last_pos % (10*1024*1024) == 0) {
                printf("Read %lld MB\n", bt->last_pos / (1024*1024));
            }

            uint8_t pc = bt->window.front();
            bt->window.pop_front();
            bt->window.push_back(c);

            bt->csum *= bt->prime;
            bt->csum += c;
            bt->csum -= pc * bt->prime_pow;
            
            if (bt->csum % bt->block_size == bt->block_indicator) {
                printf("Block at %lld\n", bt->last_pos);
                // TODO: SHA-256 hash
                *pos_ptr = bt->last_pos;
                return 0;
            }
        }

        bt->done = true;
        *pos_ptr = bt->last_pos;
        return 0;
    }
}

void endBlockify(BlockifyTask *bt) {
    fclose(bt->fp);
    delete bt;
}

}
