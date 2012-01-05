#define FUSE_USE_VERSION 26
#include <fuse.h>

#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>

#include <ctime>
#include <cstdarg>

#include <algorithm>


#include "nofs_fuse.h"

#include "logging.h"
#include "network.h"
#include "paths.h"
#include "index.h"

// Globals
int g_Socket = -1;
FILE *g_DebugFile = NULL;

// Logging
void logerror_real(const char *what, const char *func, int line) {
    if (what == NULL) {
        syslog(LOG_ERR, "%m (in %s:%d)", func, line);
    }
    else {
        syslog(LOG_ERR, "%s: %m (in %s:%d)", what, func, line);
    }
}

void debug_printf(const char *format, ...) {
    if (g_DebugFile == NULL) {
        syslog(LOG_ERR, "opening debug log");
        g_DebugFile = fopen("debug.log", "w");
    }

    char tbuf[64];
    time_t tmt = time(NULL);
    tm *tm = localtime(&tmt);
    strftime(tbuf, 63, "%H:%M:%S: ", tm);
    fwrite(tbuf, 1, strlen(tbuf), g_DebugFile);

    va_list args;
    va_start(args, format);
    vfprintf(g_DebugFile, format, args);
    va_end(args);
    fflush(g_DebugFile);
}

static int nofs_stat(const char *bundle, const char *path, struct stat *stbuf) {
    memset(stbuf, 0, sizeof(struct stat));
    stbuf->st_uid = geteuid();
    stbuf->st_gid = getegid();

    // Send request
    Header h = {{'N','F','Q'}, Header::STAT, 0, 1, 1, paths_pkt_size(bundle, path)};
    int err = h.send(g_Socket);
    if (err < 0) { logerror("send"); return -EIO; }
    err = send_paths(g_Socket, bundle, path);
    if (err < 0) { logerror("send"); return -EIO; }

    // Get response (TODO: don't allocate every time)
    const packetbuf &pb = read_packet(g_Socket, &h);
    if (h.code != 0) { DBERROR(ENOENT); }

    StatResult sr;
    try {
        mem_stream<true> ms(pb);
        StatResult::readInto(&ms, &sr);
    }
    catch (end_of_stream &e) {
        DBPRINTF("%s\n", e.what());
        DBERROR(EIO);
    }

    if (path == NULL) {
        DBPRINTF("stat %s\n", bundle);
        // Specified a bundle
        if (sr.entity_type == StatResult::Bundle) {
            stbuf->st_mode = S_IFDIR | 0755;
            stbuf->st_nlink = 2;
            DBPRINTF("result bundle\n");
            return 0;
        }
    }
    else {
        DBPRINTF("stat %s:%s\n", bundle, path);
        if (sr.entity_type == StatResult::Directory) {
            stbuf->st_mode = S_IFDIR | 0755;
            stbuf->st_nlink = 2;
            DBPRINTF("result dir\n");
            return 0;
        }
        else if (sr.entity_type == StatResult::File) {
            stbuf->st_mode = S_IFREG | 0644;
            stbuf->st_nlink = 1;
            stbuf->st_size = sr.size;
            stbuf->st_ctime = sr.ctime;
            DBPRINTF("result file, size %lu b\n", sr.size);
            return 0;
        }
    }

    DBPRINTF("result NOENT\n");
    return -ENOENT;
}


// FUSE
static int nofs_getattr(const char *rawpath, struct stat *stbuf)
{
    syslog(LOG_ERR, "nofs_getattr %s", rawpath);

    if (strcmp(rawpath, "/") == 0) {
        stbuf->st_uid = geteuid();
        stbuf->st_gid = getegid();
        stbuf->st_mode = S_IFDIR | 0755;
        stbuf->st_nlink = 2;
        return 0;
    }

    const char *bundle, *path;
    nofs_splitpath(rawpath, &bundle, &path);
    return nofs_stat(bundle, path, stbuf);
}

static int nofs_readdir(const char *rawpath, void *buf, fuse_fill_dir_t filler,
                        off_t offset, struct fuse_file_info *fi)
{
    syslog(LOG_ERR, "nofs_readdir %s", rawpath);

    if (strcmp(rawpath, "/") == 0) {
        // TODO: list bundles
        filler(buf, ".", NULL, 0);
        filler(buf, "..", NULL, 0);
        filler(buf, "inbox", NULL, 0);
        return 0;
    }
    else {
        const char *bundle, *path;
        nofs_splitpath(rawpath, &bundle, &path);

        Header h = {{'N','F','Q'}, Header::INDEX, 0, 1, 1, paths_pkt_size(bundle, path)};
        int err = h.send(g_Socket);
        if (err < 0) { return -EIO; }

        err = send_paths(g_Socket, bundle, "");
        if (err < 0) { return -EIO; }

        // Get response (TODO: don't allocate every time)
        Header::recvInto(g_Socket, &h);
        uint8_t *buffer = new uint8_t[h.payload_len];
        recv_exact(g_Socket, buffer, h.payload_len);

        if (h.code != 0) return -ENOENT;

        BundleIndex bi;
        try {
            mem_stream<true> ms(buffer, h.payload_len);
            bi.readFromPacket(&h, &ms);
        }
        catch (end_of_stream &e) {
            DBPRINTF("%s\n", e.what());
            return -EIO;
        }

        filler(buf, ".", NULL, 0);
        filler(buf, "..", NULL, 0);

        if (path == NULL) path = "";
        DBPRINTF("Filling from index at '%s'\n", path);

        const BundleIndex::Entries &ent = bi.getList(path);
        for (size_t i = 0; i < ent.size(); i++) {
            const IndexEntry &ie = ent[i];
            filler(buf, ie.name.c_str(), NULL, 0);
        }
        
        return 0;
    }
}

static int nofs_open(const char *rawpath, struct fuse_file_info *fi)
{
    const char *bundle, *path;
    nofs_splitpath(rawpath, &bundle, &path);

    DBPRINTF("open %s:%s (%X)\n", bundle, path, fi->flags);

    // TODO: can the following be taken out?
    struct stat st;
    int err = nofs_stat(bundle, path, &st);
    if (err != 0) return err;

    // NOTE: on OSX, fuse4x takes care of checking user permissions
    if ((fi->flags & O_ACCMODE) == O_RDONLY) {
        DBPRINTF("opened read only\n");
    }
    else {
        return -EACCES;
    }

    return 0;
}

static int nofs_read(const char *rawpath, char *buf, size_t size, off_t offset,
                     struct fuse_file_info *fi)
{
    const char *bundle, *path;
    bool have_path = nofs_splitpath(rawpath, &bundle, &path);

    DBPRINTF("read %s\n", rawpath);

    if (!have_path) { return -EACCES; }

    // TODO: can the following be taken out?
    struct stat st;
    int err = nofs_stat(bundle, path, &st);
    if (err != 0) return err;

    Header h = {{'N','F','Q'}, Header::READ, 0, 1, 1, paths_pkt_size(bundle, path)};
    err = h.send(g_Socket);
    if (err < 0) { logerror("send"); return -EIO; }

    err = send_paths(g_Socket, bundle, path);
    if (err < 0) { logerror("send_paths"); return -EIO; }

    // Read the entire file into memory
    std::vector<uint8_t> buffer;

    int total_pkts = 1;
    for (int ix_packet = 0; ix_packet < total_pkts; ix_packet++) {
    	Header::recvInto(g_Socket, &h);
    	total_pkts = h.total_packets;
    	size_t prev_size = buffer.size();
    	buffer.resize(prev_size + h.payload_len);
    	if (recv_exact(g_Socket, &buffer[prev_size], h.payload_len) == false) {
    		logerror("recv_exact");
    		return -EIO;
    	}
    }

    // Now spit out the part requested (TODO: large files)
    size_t real_size = std::min(size, (size_t)(buffer.size() - offset));
    memcpy(buf, &buffer[offset], real_size);
    return real_size;
}

static struct fuse_operations nofs_oper;

int main(int argc, char *argv[])
{
    bool seen_st = false;
    for (int i = 0; i < argc; i++) {
        if (strcmp(argv[i], "-s") == 0) {
            seen_st = true;
            break;
        }
    }

    if (!seen_st) {
        printf("Please pass single-threaded option (-s)\n");
        exit(1);
    }

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
    //int sa_len = sizeof(sa.sun_family) + strlen(sa.sun_path);

    // Connect
    if (connect(g_Socket, (struct sockaddr *)&sa, sizeof(struct sockaddr_un)) == -1) {
        logerror("connect");
        exit(1);
    }

    syslog(LOG_ERR, "Connected!");
    DBPRINTF("Starting FUSE\n");

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
