#ifndef H_NETWORK
#define H_NETWORK

#include <vector>

extern bool recv_exact(int sock, uint8_t *buf, size_t size);

extern size_t paths_pkt_size(const char *bundle, const char *path);
extern int send_paths(int s, const char *bundle, const char *path);


#include "packet.h"

typedef std::vector<uint8_t> packetbuf;
extern const packetbuf &read_packet(int s, Header *h);

#endif
