#include <stdint.h>
#include <sys/socket.h>
#include <cstring>

#include <vector>

#include "network.h"
#include <google/protobuf/io/zero_copy_stream_impl.h>

static std::vector<uint8_t> g_Packet;
static google::protobuf::io::ArrayInputStream g_VecBuf(NULL, 0);

void start_packet() {
    g_Packet.clear();
}

void add_pbuf(::google::protobuf::Message *msg) {
    std::string str;
    msg->SerializeToString(&str);

    size_t path_size = str.size();
    size_t curr_size = g_Packet.size();
    g_Packet.resize(curr_size + path_size);
    memcpy(&g_Packet[curr_size], str.c_str(), path_size);
}

int send_packet(int sock, Header *h) {
    h->payload_len = g_Packet.size();
    int err = send(sock, h, sizeof(Header), 0);
    if (err < 0) return err;
    err = send(sock, &g_Packet[0], g_Packet.size(), 0);
    return err;
}

typedef google::protobuf::io::ArrayInputStream AIS;
shared_ptr<pkt_stream> recv_packet(int sock, Header *h) {
    uint8_t *packet = recv_packet_raw(sock, h);
    shared_ptr<pkt_stream> ais(new AIS(&g_Packet[0], g_Packet.size()));
    return ais;
}

uint8_t *recv_packet_raw(int sock, Header *h) {
    int err = recv(sock, h, sizeof(Header), MSG_WAITALL);
    if (err < 0) return NULL;
    if (g_Packet.size() < h->payload_len) {
        g_Packet.resize(h->payload_len);
    }

    err = recv(sock, &g_Packet[0], h->payload_len, MSG_WAITALL);
    if (err < 0) return NULL;
    return &g_Packet[0];
}
