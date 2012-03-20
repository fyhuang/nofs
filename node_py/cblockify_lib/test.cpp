#include "cblockify.cpp"

#include <cstdio>
#include <fcntl.h>

int main(int argc, char *argv[]) {
    int fd = open("/Users/fyhuang/Desktop/test.iso", O_RDONLY);
    BlockifyTask *bt = beginBlockify(fd);

    uint64_t nb = nextBlock(bt);
    while (nb != 0) {
        nb = nextBlock(bt);
    }
    endBlockify(bt);

    return 0;
}
