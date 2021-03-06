#define FUSE_USE_VERSION 26
#include <fuse.h>

#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>

#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <syslog.h>

#include <ctime>
#include <cstdarg>
#include <cstdio>
#include <cstdlib>
#include <cstring>

#include <stdint.h>
#include <limits.h>


#include "logging.h"
#include "network.h"

// Globals
int g_Socket = -1;
FILE *g_DebugFile = NULL;

void _debug_printf(const char *func, int line, const char *format, ...) {
    if (g_DebugFile == NULL) {
        //syslog(LOG_ERR, "opening debug log");
        g_DebugFile = fopen("debug.log", "w");
    }

    char tbuf[64];
    time_t tmt = time(NULL);
    tm *tm = localtime(&tmt);
    strftime(tbuf, 63, "%H:%M:%S ", tm);
    fwrite(tbuf, 1, strlen(tbuf), g_DebugFile);
    fprintf(g_DebugFile, "%s:%d: ", func, line);

    va_list args;
    va_start(args, format);
    vfprintf(g_DebugFile, format, args);
    va_end(args);
    fflush(g_DebugFile);
}

void _syslog_error(const char *what, const char *func, int line) {
    char buffer[512];
    strcpy(buffer, what);
    strcat(buffer, " (in %s:%d)");
    syslog(LOG_ERR, buffer, func, line);
    DBPRINTF("%s\n", what);
}


// FUSE functions
static int nofs_stat(const char *path, struct stat *stbuf) {
    memset(stbuf, 0, sizeof(struct stat));
    stbuf->st_uid = geteuid();
    stbuf->st_gid = getegid();

    nofs_local::ReqStat req_stat;
    req_stat.set_filepath(path);

    // Send request
    start_packet();
    add_pbuf(&req_stat);

    Header h = {REQ_STAT, 0};
    int err = send_packet(g_Socket, &h);
    if (err < 0) {
        LOGERROR("send %m");
        return -EIO;
    }

    // Get response
    shared_ptr<pkt_stream> pdata = recv_packet(g_Socket, &h);
    if (!pdata) {
        LOGERROR("recv %m");
        return -EIO;
    }

    if (h.pkt_type == RESP_ERROR) {
        LOGERROR("error");
        // TODO
        return -ENOENT;
    }

    DBPRINTF("stat %s\n", path);
    nofs_local::RespStat sr;
    sr.ParseFromZeroCopyStream(pdata.get());

    if (sr.ftype() & S_IFDIR) {
        stbuf->st_mode = S_IFDIR | 0755;
        stbuf->st_nlink = 2;
        stbuf->st_ino = sr.inode();
        DBPRINTF("result dir\n");
        return 0;
    }
    else if (sr.ftype() & S_IFREG) {
        stbuf->st_mode = S_IFREG | 0644;
        stbuf->st_nlink = 1;
        stbuf->st_size = sr.size();
        stbuf->st_ino = sr.inode();

        time_t ctime_utc = sr.ctime_utc();
        struct tm *tm_loc = localtime(&ctime_utc);
        stbuf->st_ctime = mktime(tm_loc);
        DBPRINTF("result file, size %lu b\n", sr.size());
        //DBPRINTF("ctime_utc %d, ctime %d, %s", ctime_utc, stbuf->st_ctime, ctime(&ctime_utc));
        return 0;
    }

    DBPRINTF("result NOENT\n");
    return -ENOENT;
}


// FUSE
static int nofs_getattr(const char *path, struct stat *stbuf)
{
    DBPRINTF("nofs_getattr %s\n", path);

    if (strcmp(path, "/") == 0) {
        stbuf->st_uid = geteuid();
        stbuf->st_gid = getegid();
        stbuf->st_mode = S_IFDIR | 0755;
        stbuf->st_nlink = 2;
        return 0;
    }

    return nofs_stat(path, stbuf);
}

static int nofs_readdir(const char *path, void *buf, fuse_fill_dir_t filler,
                        off_t offset, struct fuse_file_info *fi)
{
    DBPRINTF("nofs_readdir %s\n", path);

    ReqListdir req_listdir;
    req_listdir.set_dirpath(path);
    start_packet();
    add_pbuf(&req_listdir);

    Header h = {REQ_LISTDIR, 0};
    int err = send_packet(g_Socket, &h);
    if (err < 0) {
        LOGERROR("send %m");
        return -EIO;
    }

    shared_ptr<pkt_stream> pdata = recv_packet(g_Socket, &h);
    if (!pdata) {
        LOGERROR("recv %m");
        return -EIO;
    }

    if (h.pkt_type == RESP_ERROR) {
        // TODO
        return -ENOENT;
    }

    filler(buf, ".", NULL, 0);
    filler(buf, "..", NULL, 0);

    RespListdir rl;
    rl.ParseFromZeroCopyStream(pdata.get());

    for (int i = 0; i < rl.entry_size(); i++) {
        DBPRINTF("Reading entry %d\n", i);
        const RespListdir::ListdirEntry &entry = rl.entry(i);
        filler(buf, entry.filename().c_str(), NULL, 0);
    }

    return 0;
}

static int nofs_open(const char *path, struct fuse_file_info *fi)
{
    DBPRINTF("open %s (%X)\n", path, fi->flags);

    // TODO: can the following be taken out?
    struct stat st;
    int err = nofs_stat(path, &st);
    if (err != 0) return err;

    // NOTE: on OSX, fuse4x takes care of checking user permissions
    // TODO: check behavior on Linux
    if ((fi->flags & O_ACCMODE) == O_RDONLY) {
        DBPRINTF("opened read only\n");
    }
    else {
        return -EACCES;
    }

    return 0;
}

static int nofs_read(const char *path, char *buf, size_t size, off_t offset,
                     struct fuse_file_info *fi)
{
    DBPRINTF("read %s\n", path);

    // TODO: can the following be taken out?
    struct stat st;
    int err = nofs_stat(path, &st);
    if (err != 0) return err;

    // TODO
    if (size > ULONG_MAX - sizeof(Header) - 1) {
        size = ULONG_MAX - sizeof(Header) - 1;
    }

    ReqRead req_read;
    req_read.set_filepath(path);
    req_read.set_offset(offset);
    req_read.set_length(size);
    start_packet();
    add_pbuf(&req_read);
    Header h = {REQ_READ, 0};
    err = send_packet(g_Socket, &h);
    if (err < 0) {
        LOGERROR("send %m");
        return -EIO;
    }

    uint8_t *pdata = recv_packet_raw(g_Socket, &h);
    if (pdata == NULL) {
        LOGERROR("recv %m");
        return -EIO;
    }

    size_t real_size = h.payload_len;
    memcpy(buf, pdata, real_size);
    return real_size;
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

    if (argc < 3) {
        printf("not enough arguments!\n");
        exit(1);
    }

    g_Socket = socket(AF_UNIX, SOCK_STREAM, 0);
    if (g_Socket < 0) {
        LOGERROR("socket %m");
        exit(1);
    }

    struct sockaddr_un sa;
    sa.sun_family = AF_UNIX;
    strcpy(sa.sun_path, argv[1]);

    // Connect
    if (connect(g_Socket, (struct sockaddr *)&sa, sizeof(struct sockaddr_un)) == -1) {
        LOGERROR("connect %m");
        exit(1);
    }

    // Send protocol request
    const char *proto_info = "LOCAL";
    send(g_Socket, proto_info, strlen(proto_info), 0);

    DBPRINTF("Connected!\n");
    DBPRINTF("Header size: %d\n", sizeof(Header));

    /*while (true) {
        Header h = {REQ_READ, 0};
        start_packet();
        add_uint64(10);
        add_uint32(20);
        add_path("/inbox/pic.jpg");
        int err = send_packet(g_Socket, &h);
        if (err < 0) {
            LOGERROR("send %m");
            exit(1);
        }

        uint8_t *pdata = recv_packet(g_Socket, &h);
        if (pdata == NULL) {
            LOGERROR("recv %m");
            exit(1);
        }*/

        //printf("%d\n", h.payload_len);

        /*uint32_t num_entries = *((uint32_t*)pdata);
        printf("num_entries: %d\n", num_entries);
        size_t ix = 4;
        for (uint32_t i = 0; i < num_entries; i++) {
            if (ix >= h.payload_len) {
                printf("ERROR END OF PACKET\n");
                break;
            }
            uint32_t path_size = *((uint32_t*)(pdata+ix));
            ix += 4;
            char *buffer = new char[path_size+1];
            memcpy(buffer, pdata+ix, path_size);
            buffer[path_size] = '\0';
            ix += path_size;
            printf("%s ", buffer);
            delete[] buffer;

            RespStat *resp = (RespStat *)(pdata+ix);
            printf("%c %d %d %d %d\n",
                    resp->ftype,
                    resp->perms,
                    resp->inode,
                    resp->size,
                    resp->ctime_utc);
            ix += sizeof(RespStat);
        }*/

        /*RespStat *resp = (RespStat *)pdata;
        printf("%c %d %d %d %d\n",
                resp->ftype,
                resp->perms,
                resp->inode,
                resp->size,
                resp->ctime_utc);*/

        /*sleep(1);
    }
    return 0;*/

    // TODO: just hardcode the needed arguments to FUSE
    // TODO: pass -s option (single-threaded)
    int fuse_argc = 3;
    char *fuse_argv[] = {argv[0], "-s", argv[2]};
    return fuse_main(fuse_argc, fuse_argv, &nofs_oper, NULL);
}
