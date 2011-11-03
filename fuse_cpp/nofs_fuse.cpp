#define FUSE_USE_VERSION 26
#include <fuse.h>

#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <syslog.h>

#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>

#include <string>


#include "nofs_fuse.h"

// Globals
int g_Socket = -1;
static SocketReader *g_Reader = NULL;

// Logging
void logerror(const char *what) {
    if (what == NULL) {
        syslog(LOG_ERR, "%m");
    }
    else {
        syslog(LOG_ERR, "%s: %m", what);
    }
}

// FUSE
/// @returns true if a path into the bundle was provided
static bool nofs_splitpath(const char *input, std::string &bundle, std::string &path)
{
    syslog(LOG_ERR, "nofs_splitpath %s", input);
    // free() the strings returned by this func
    const char *after_bundle = strchr(input + 1, '/');
    if (after_bundle != NULL) {
        path = std::string(after_bundle + 1);

        size_t bsize = after_bundle - input - 1;
        bundle = std::string(bsize, '\0');
        memcpy(&bundle[0], input + 1, size);
        return true;
    }
    else {
        path = std::string();
        bundle = std::string(input + 1);
        return false;
    }
}

static AppendBuffer *nofs_syncrt(const char *packet)
{
    if (send(g_Socket, packet, strlen(packet), 0) < 0) {
        logerror("send");
        return NULL;
    }

    syslog(LOG_ERR, "reading packet");

    AppendBuffer *ab = g_Reader->nextJSON();
    if (ab == NULL) {
        syslog(LOG_ERR, "couldn't read packet");
        return NULL;
    }

    return ab;
}

static int nofs_getattr(const char *rawpath, struct stat *stbuf)
{
    syslog(LOG_ERR, "nofs_getattr %s", rawpath);
    memset(stbuf, 0, sizeof(struct stat));

    if (strcmp(rawpath, "/") == 0) {
        stbuf->st_mode = S_IFDIR | 0755;
        stbuf->st_nlink = 2;
        return 0;
    }

    std::string bundle, path;
    bool have_path = nofs_splitpath(rawpath, &bundle, &path);

    char buffer[512];
    if (path == NULL) {
        syslog(LOG_ERR, "getattr bundle %s", bundle);
        // Specified a bundle
        snprintf(buffer, 512, "{\"action\":\"stat\",\"RequestId\": 0, \"bundle\":\"%s\"}", bundle);
        AppendBuffer *ab = nofs_syncrt(buffer);
        if (ab == NULL) return -EIO;

        const char *packet = ab->toString();
        syslog(LOG_ERR, "got packet %s", packet);

        if (strstr(packet, "Success") == NULL) {
            syslog(LOG_ERR, "operation failed");
            return -ENOENT;
        }

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
    syslog(LOG_ERR, "nofs_readdir %s", path);

    char buffer[512];
    if (strcmp(rawpath, "/") == 0) {
        snprintf(buffer, 512, "{\"action\":\"index\", \"RequestId\": 0, \"SimpleOutput\": true}");
    }

    if (strcmp(path, "/") != 0)
        return -ENOENT;

    // TODO
    filler(buf, ".", NULL, 0);
    filler(buf, "..", NULL, 0);
    filler(buf, "inbox", NULL, 0);

    return 0;
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

    // Initialize globals
    g_Reader = new SocketReader(g_Socket);
    
    while (true) {
        // Send some data
        const char *data = "{\"action\":\"stat\", \"bundle\":\"inbox\"}";
        int err = send(g_Socket, data, strlen(data), 0);
        if (err < 0) {
            perror("nofs: sendto");
            exit(1);
        }

        printf("Sent!\n");

        // Receive a JSON packet
        AppendBuffer *ab = g_Reader->nextJSON();
        const char *json = ab->toString();
        printf("Read JSON: %s\n", json);
        delete ab;

        sleep(1);
    }
    return 0;
    //return fuse_main(argc, argv, &nofs_oper, NULL);
}
