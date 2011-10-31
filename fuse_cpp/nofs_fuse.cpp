#include "protos.h"

#define FUSE_USE_VERSION 26
#include <fuse.h>

#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <syslog.h>

#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>

// Globals
int g_Socket = -1;

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
static void nofs_splitpath(const char *input, char **bundle, char **path)
{
    syslog(LOG_ERR, "nofs_splitpath %s", input);
    // free() the strings returned by this func
    const char *after_bundle = strchr(input + 1, '/');
    if (after_bundle != NULL) {
        *path = strdup(after_bundle + 1);

        size_t size = after_bundle - input - 1;
        *bundle = malloc(size + 1);
        memcpy(*bundle, input + 1, size);
    }
    else {
        *path = NULL;
        *bundle = strdup(input + 1);
    }
}

static int nofs_getattr(const char *rawpath, struct stat *stbuf)
{
    syslog(LOG_ERR, "nofs_getattr %s", rawpath);
    memset(stbuf, 0, sizeof(struct stat));

    int res = 0;
    if (strcmp(rawpath, "/") == 0) {
        stbuf->st_mode = S_IFDIR | 0755;
        stbuf->st_nlink = 2;
        return 0;
    }
    else {
        char *bundle, *path;
        nofs_splitpath(rawpath, &bundle, &path);

        char buffer[512];
        if (path == NULL) {
            syslog(LOG_ERR, "getattr bundle %s", bundle);
            // Specified a bundle directory
            snprintf(buffer, 512, "{\"action\":\"stat\",\"bundle\":\"%s\"}", bundle);
            if (send(g_Socket, buffer, strlen(buffer), 0) < 0) {
                logerror("send");
                return -EIO;
            }

            syslog(LOG_ERR, "reading packet");

            const char *packet = Socket_ReadJSON(g_Socket);
            if (packet == NULL) {
                syslog(LOG_ERR, "couldn't read packet");
                return -EIO;
            }

            syslog(LOG_ERR, "got packet %s", packet);

            if (strstr(packet, "Success") == NULL) {
                syslog(LOG_ERR, "no success found");
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
}

static int nofs_readdir(const char *path, void *buf, fuse_fill_dir_t filler,
                        off_t offset, struct fuse_file_info *fi)
{
    syslog(LOG_ERR, "nofs_readdir %s", path);
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

static struct fuse_operations nofs_oper = {
    .getattr = nofs_getattr,
    .readdir = nofs_readdir,
    .open = nofs_open,
    .read = nofs_read,
};


int main(int argc, char *argv[])
{
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
    g_AppendBuffer = AB_New(BUFFER_LENGTH);
    
    /*while (true) {
        // Send some data
        const char *data = "{\"action\":\"stat\", \"bundle\":\"inbox\"}";
        int err = send(g_Socket, data, strlen(data), 0);
        if (err < 0) {
            perror("nofs: sendto");
            exit(1);
        }

        printf("Sent!\n");

        // Receive a JSON packet
        const char *json = Socket_ReadJSON(g_Socket);
        printf("Read JSON: %s\n", json);

        sleep(1);
    }
    return 0;*/
    return fuse_main(argc, argv, &nofs_oper, NULL);
}
