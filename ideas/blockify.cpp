#include <boost/circular_buffer.hpp>

#include <cstdio>
#include <cstdlib>
#include <stdint.h>

uint32_t ipow(uint32_t base, uint32_t exp) {
    uint32_t accum = 1;
    for (uint32_t i = 0; i < exp; i++) {
        accum *= base;
    }
    return accum;
}

void blockify(FILE *fp) {
    const int prime = 139;
    const int window_size = 31;
    const int block_size = 8192;
    const long int limit = 32*1024*1024;

    boost::circular_buffer<uint8_t> window(window_size);
    for (int i = 0; i < window_size; i++) {
        window.push_back(0);
    }

    uint32_t num_blocks = 0;
    uint32_t csum = 1;

    uint32_t prime_pow = ipow(prime, window_size);

    int c;
    while (true) {
        c = fgetc(fp);
        if (c == EOF) break;
        if (ftell(fp) > limit) break;

        char pc = window.front();
        window.pop_front();
        window.push_back(c);

        csum *= prime;
        csum += c;
        csum -= pc * prime_pow;
        
        if (csum % block_size == 0) {
            printf("Block at %d\n", ftell(fp));
            num_blocks++;
        }
    }

    printf("Num blocks: %d\n", num_blocks);
}

int main(int argc, char *argv[]) {
    FILE *fp = fopen("test.iso", "rb");
    blockify(fp);
    fclose(fp);
    return 0;
}
