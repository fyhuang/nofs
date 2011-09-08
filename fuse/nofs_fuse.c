#include "protos.h"
//#include <fuse.h>

#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>

/*static struct fuse_operations nofs_oper = {
};*/

// Globals
int g_Socket = -1;
uint8 *g_Leftover = NULL;
AppendBuffer *g_AppendBuffer = NULL;

int main(int argc, char *argv[])
{
    int s = socket(AF_UNIX, SOCK_STREAM, 0);
    if (s < 0) {
        perror("nofs: socket");
        exit(1);
    }

    struct sockaddr_un sa;
    sa.sun_family = AF_UNIX;
    strcpy(sa.sun_path, "/tmp/nofs.socket");
    int sa_len = sizeof(sa.sun_family) + strlen(sa.sun_path);

    // Connect
    if (connect(s, (struct sockaddr *)&sa, sizeof(struct sockaddr_un)) == -1) {
        perror("nofs: connect");
        exit(1);
    }

    // Initialize globals
    g_AppendBuffer = AB_New(BUFFER_LENGTH);
    
    while (true) {
        // Send some data
        const char *data = "{\"action\":\"read\", \"bundle\":\"inbox\", \"filename\":\"test.txt\"}";
        int err = send(s, data, strlen(data), 0);
        if (err < 0) {
            perror("nofs: sendto");
            exit(1);
        }

        printf("Sent!\n");

        // Receive a JSON packet
        const char *json = Socket_ReadJSON(s);
        printf("Read JSON: %s\n", json);

        sleep(1);
    }

    return 0;

    //return fuse_main(argc, argv, &nofs_oper);
}
