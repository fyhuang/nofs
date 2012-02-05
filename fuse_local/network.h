#pragma pack(push, 4)
enum {
    REQ_STAT = 1,
    REQ_LISTDIR,
    REQ_READ,

    RESP_ERROR = 0,

    RESP_STAT = 128,
    RESP_LISTDIR,
    RESP_READ
};

struct Header {
    uint32_t pkt_type;
    uint32_t payload_len;
};

struct RespStat {
    char ftype;
    uint8_t perms;
    uint32_t inode;
    uint64_t size;
    uint64_t ctime_utc;
};
#pragma pack(pop)

// Packet building
extern void start_packet();
extern void add_path(const char *path); // TODO: unicode
extern void add_uint32(uint32_t val);
extern void add_uint64(uint64_t val);
extern int send_packet(int sock, Header *h);

extern uint8_t *recv_packet(int sock, Header *h);
