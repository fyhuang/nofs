#include <stdint.h>
#include <sys/socket.h>
#include <cstring>

#include <vector>

#include "network.h"

static std::vector<uint8_t> g_Packet;

void start_packet() {
    g_Packet.clear();
}

void add_path(const char *path) {
    size_t path_size = strlen(path);
    add_uint32(path_size);
    size_t curr_size = g_Packet.size();
    g_Packet.resize(curr_size + path_size);
    memcpy(&g_Packet[curr_size], path, path_size);
}

void add_uint32(uint32_t val) {
    size_t curr_size = g_Packet.size();
    g_Packet.resize(curr_size + 4);
    memcpy(&g_Packet[curr_size], &val, 4);
}

void add_uint64(uint64_t val) {
    size_t curr_size = g_Packet.size();
    g_Packet.resize(curr_size + 8);
    memcpy(&g_Packet[curr_size], &val, 8);
}

int send_packet(int sock, Header *h) {
    h->payload_len = g_Packet.size();
    int err = send(sock, h, sizeof(Header), 0);
    if (err < 0) return err;
    err = send(sock, &g_Packet[0], g_Packet.size(), 0);
    return err;
}

uint8_t *recv_packet(int sock, Header *h) {
    int err = recv(sock, h, sizeof(Header), MSG_WAITALL);
    if (err < 0) return NULL;
    if (g_Packet.size() < h->payload_len) {
        g_Packet.resize(h->payload_len);
    }

    err = recv(sock, &g_Packet[0], h->payload_len, MSG_WAITALL);
    if (err < 0) return NULL;
    return &g_Packet[0];
}
