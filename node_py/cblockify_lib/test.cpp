#include "cblockify.cpp"

#include <cstdio>
#include <fcntl.h>

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: test filename\n");
        return -1;
    }

    //BlockifyTask *bt = beginBlockify("/Users/fyhuang/Desktop/test.iso");
    BlockifyTask *bt = beginBlockify(argv[1]);
    if (bt == NULL) {
        printf("Error\n");
        return -1;
    }

    char buffer[256];
    bool cont = nextBlock(bt, buffer);
    while (cont == 0) {
        cont = nextBlock(bt, buffer);
    }
    endBlockify(bt);

    return 0;
}
