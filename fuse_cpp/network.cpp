#include "nofs_fuse.h"
#include "network.h"
#include "logging.h"

std::vector<uint8_t> g_Buffer;

/// @returns false if an error occurred
bool recv_exact(int sock, uint8_t *buf, size_t size) {
    size_t total = 0;
    while (total < size) {
        int rd = recv(sock, buf+total, size, 0);
        if (rd <= 0) {
            return false;
        }
        total += rd;
    }
    return true;
}

size_t paths_pkt_size(const char *bundle, const char *path) {
	if (path == NULL) return strlen(bundle) + 4;
	return strlen(bundle) + strlen(path) + 4;
}

int send_paths(int sock, const char *bundle, const char *path) {
    uint16_t len = htons(strlen(bundle));
    int err = send(sock, &len, sizeof(uint16_t), 0);
    if (err < 0) { logerror("send"); return err; }

    if (path != NULL) {
        len = htons(strlen(path));
    }
    else {
        len = 0;
    }
    err = send(sock, &len, sizeof(uint16_t), 0);
    if (err < 0) { logerror("send"); return err; }

    err = send(sock, bundle, strlen(bundle), 0);
    if (err < 0) { logerror("send"); return err; }

    if (path != NULL) {
        err = send(sock, path, strlen(path), 0);
        if (err < 0) { logerror("send"); return err; }
    }

    return 0;
}

const std::vector<uint8_t> &read_packet(int s, Header *h)
{
	Header::recvInto(s, h);
	if (h->total_packets > 1) {
		DBPRINTF("%d of %d packets", h->packet_num, h->total_packets);
	}

	g_Buffer.resize(h->payload_len);
	recv_exact(s, &g_Buffer[0], h->payload_len);
    return g_Buffer;
}
