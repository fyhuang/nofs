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
#pragma pack(pop)

#include <boost/shared_ptr.hpp>
using boost::shared_ptr;

// Protocol buffers
#include <google/protobuf/io/zero_copy_stream.h>
#include "proto/nofs_local.pb.h"
using namespace nofs_local;

// Packet building
extern void start_packet();
extern void add_pbuf(::google::protobuf::Message *msg);
extern int send_packet(int sock, Header *h);

typedef google::protobuf::io::ZeroCopyInputStream pkt_stream;
extern shared_ptr<pkt_stream> recv_packet(int sock, Header *h);
extern uint8_t *recv_packet_raw(int sock, Header *h);
