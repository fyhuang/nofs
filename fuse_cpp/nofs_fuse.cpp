#define FUSE_USE_VERSION 26
#include <fuse.h>

#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>


#include "nofs_fuse.h"

// Globals
int g_Socket = -1;

std::vector<uint8_t> g_Buffer;

// Logging
void logerror(const char *what) {
    if (what == NULL) {
        syslog(LOG_ERR, "%m");
    }
    else {
        syslog(LOG_ERR, "%s: %m", what);
    }
}

bool recv_exact(int sock, uint8_t *buf, size_t size) {
    int total = 0;
    while (total < size) {
        int rd = recv(sock, buf+total, size, 0);
        if (rd <= 0) {
            return false;
        }
        total += rd;
    }
    return true;
}

int send_paths(int sock, const char *bundle, const char *path) {
    uint16_t len = htons(strlen(bundle));
    send(sock, &len, sizeof(uint16_t), 0);
    len = htons(strlen(path));
    send(sock, &len, sizeof(uint16_t), 0);

    send(sock, bundle, strlen(bundle), 0);
    send(sock, path, strlen(path), 0);

    return 0; // TODO
}

static std::vector<uint8_t> *nofs_exch(uint8_t *packet)
{
    const char *ccp = (const char *)packet;
    if (send(g_Socket, ccp, strlen(ccp), 0) < 0) {
        logerror("send");
        return NULL;
    }

    syslog(LOG_ERR, "reading packet");

    Header header;
    Header::recvInto(g_Socket, &header);
    printf("%d of %d packets", header.packet_num, header.total_packets);

    // TODO
    return &g_Buffer;
}


// FUSE
static int nofs_getattr(const char *rawpath, struct stat *stbuf)
{
    syslog(LOG_ERR, "nofs_getattr %s", rawpath);
    memset(stbuf, 0, sizeof(struct stat));

    if (strcmp(rawpath, "/") == 0) {
        stbuf->st_mode = S_IFDIR | 0755;
        stbuf->st_nlink = 2;
        return 0;
    }

    char *bundle, *path;
    bool have_path = nofs_splitpath(rawpath, &bundle, &path);

    if (!have_path) {
        syslog(LOG_ERR, "getattr bundle %s", bundle);
        // Specified a bundle
        stbuf->st_mode = S_IFDIR | 0755;
        stbuf->st_nlink = 2;
        syslog(LOG_ERR, "found bundle?");
        return 0;
    }
    else {
        syslog(LOG_ERR, "getattr bundle %s path %s\n", bundle, path);
        return -ENOENT;
    }
}

static int nofs_readdir(const char *rawpath, void *buf, fuse_fill_dir_t filler,
                        off_t offset, struct fuse_file_info *fi)
{
    syslog(LOG_ERR, "nofs_readdir %s", rawpath);

    char buffer[512];
    if (strcmp(rawpath, "/") == 0) {
        // TODO: list bundles
        filler(buf, ".", NULL, 0);
        filler(buf, "..", NULL, 0);
        filler(buf, "inbox", NULL, 0);
        return 0;
    }
    else {
        char *bundle, *path;
        if (nofs_splitpath(rawpath, &bundle, &path) == true) {
            return -ENOENT;
        }

        Header h = {{'N','F','Q'}, Header::INDEX, 0, 1, 1, 0};
        int err = h.send(g_Socket);
        if (err < 0) { return -EIO; }

        err = send_paths(g_Socket, bundle, "");
        if (err < 0) { return -EIO; }

        // Get response (TODO: don't allocate every time)
        Header::recvInto(g_Socket, &h);
        uint8_t *buffer = new uint8_t[h.payload_len];
        recv_exact(g_Socket, buffer, h.payload_len);

        if (h.code != 0) return -ENOENT;

        filler(buf, ".", NULL, 0);
        filler(buf, "..", NULL, 0);

        mem_stream<true> ms(buffer, h.payload_len);
        size_t num_entries = ms.read4();
        for (size_t i = 0; i < num_entries; i++) {
            IndexEntry ie;
            IndexEntry::readInto(&ms, &ie);
            filler(buf, ie.name.c_str(), NULL, 0);
        }
        
        return 0;
    }
}

static int nofs_open(const char *path, struct fuse_file_info *fi)
{
    return 0;
}

static int nofs_read(const char *path, char *buf, size_t size, off_t offset,
                     struct fuse_file_info *fi)
{
    return 0;
}

static struct fuse_operations nofs_oper;

int main(int argc, char *argv[])
{
    // Setup FUSE pointers
    nofs_oper.getattr = nofs_getattr;
    nofs_oper.readdir = nofs_readdir;
    nofs_oper.open = nofs_open;
    nofs_oper.read = nofs_read;

    openlog("nofs", LOG_CONS, LOG_USER);

    g_Socket = socket(AF_UNIX, SOCK_STREAM, 0);
    if (g_Socket < 0) {
        logerror("socket");
        exit(1);
    }

    struct sockaddr_un sa;
    sa.sun_family = AF_UNIX;
    strcpy(sa.sun_path, "/tmp/nofs.socket");
    int sa_len = sizeof(sa.sun_family) + strlen(sa.sun_path);

    // Connect
    if (connect(g_Socket, (struct sockaddr *)&sa, sizeof(struct sockaddr_un)) == -1) {
        logerror("connect");
        exit(1);
    }

    syslog(LOG_ERR, "Connected!");

    /*while (true) {
        // Send some data
        Header h = {{'N','F','Q'}, Header::INDEX, 0, 1, 1, 0};
        int err = h.send(g_Socket);
        if (err < 0) {
            perror("nofs: sendto");
            exit(1);
        }

        send_paths(g_Socket, "inbox", "");

        printf("Sent!\n");

        // Receive a packet
        Header::recvInto(g_Socket, &h);
        printf("Code %d, %d of %d packets\n", h.code, h.packet_num, h.total_packets);
        printf("\tLen %d\n", h.payload_len);
        uint8_t *buffer = new uint8_t[h.payload_len];
        recv_exact(g_Socket, buffer, h.payload_len);

        mem_stream<true> ms(buffer, h.payload_len);
        size_t num_entries = ms.read4();
        for (size_t i = 0; i < num_entries; i++) {
            IndexEntry ie;
            IndexEntry::readInto(&ms, &ie);
            printf("\tIndex entry: %s\n", ie.name.c_str());
            printf("\tStat result: %d\n", ie.stat.entity_type);
        }

        delete[] buffer;

        sleep(1);
    }
    return 0;*/
    return fuse_main(argc, argv, &nofs_oper, NULL);
}
