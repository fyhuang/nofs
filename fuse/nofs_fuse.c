#include <stdio.h>
#include <stdlib.h>
#include <string.h>
//#include <fuse.h>

#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>

/*static struct fuse_operations nofs_oper = {
};*/

#define BUFFER_LENGTH 128*1024

int main(int argc, char *argv[])
{
    int s = socket(AF_UNIX, SOCK_DGRAM, 0);
    if (s < 0) {
        perror("nofs: socket");
        exit(1);
    }

    struct sockaddr_un sa;
    sa.sun_family = AF_UNIX;
    strcpy(sa.sun_path, "/tmp/nofs.socket");
    int sa_len = sizeof(sa.sun_family) + strlen(sa.sun_path);
    
    const char *data = "{\"action\":\"read\", \"bundle\":\"inbox\", \"filename\":\"test.txt\"}";
    int err = sendto(s, data, strlen(data), 0, (struct sockaddr *)(&sa), sizeof(struct sockaddr_un));
    if (err < 0) {
        perror("nofs: sendto");
        exit(1);
    }

    printf("Sent!\n");

    unsigned char *buffer = malloc(BUFFER_LENGTH);
    struct sockaddr_storage recv_sa;
    int recv_sa_len = 0;
    int recv_len = recvfrom(s, buffer, BUFFER_LENGTH, 0, (struct sockaddr *)&recv_sa, &recv_sa_len);
    if (recv_len < 0) {
        perror("nofs: recvfrom");
        free(buffer);
        exit(1);
    }

    for (int i = 0; i < recv_len; i++) {
        putc(buffer[i], stdout);
    }
    printf("\n");

    return 0;

    //return fuse_main(argc, argv, &nofs_oper);
}
