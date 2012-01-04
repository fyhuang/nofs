#ifndef H_PACKET
#define H_PACKET

#include <arpa/inet.h>

#include "mem_stream.h"

struct Header {
    unsigned char magic[3];
    enum { STAT=1, INDEX=2, READ=3, STOP=255 };
    uint8_t code;
    uint32_t req_id;

    uint16_t total_packets;
    uint16_t packet_num;

    uint32_t payload_len;


    int send(int sock) {
        // TODO: this invalidates this header
        hton();
        return ::send(sock, this, sizeof(Header), 0);
    }

    void hton() {
        req_id = htonl(req_id);
        total_packets = htons(total_packets);
        packet_num = htons(packet_num);
        payload_len = htonl(payload_len);
    }

    void ntoh() {
        req_id = ntohl(req_id);
        total_packets = ntohs(total_packets);
        packet_num = ntohs(packet_num);
        payload_len = ntohl(payload_len);
    }

    static bool recvInto(int sock, Header *h) {
        const size_t hs = sizeof(Header);
        memset(h, 0, hs);
        
        uint8_t buf[hs];
        if (!recv_exact(sock, buf, hs)) {
            return false;
        }

        memcpy(h, buf, hs);
        h->ntoh();
        return true;
    }
};

struct StatResult {
    enum { File, Directory, Bundle } entity_type;
    uint64_t ctime;
    uint64_t size;

    static bool readInto(mem_stream<true> *str, StatResult *r) {
        // TODO: padding
        for (int i = 0; i < 3; i++) str->read1();

        char type = str->read1();
        switch (type) {
        case 'f':
            r->entity_type = File;
            break;
        case 'd':
            r->entity_type = Directory;
            break;
        case 'b':
            r->entity_type = Bundle;
            break;
        }

        r->ctime = str->read8();
        r->size = str->read8();

        return true;
    }
};

struct IndexEntry {
    std::string name;
    StatResult stat;

    static bool readInto(mem_stream<true> *str, IndexEntry *e) {
        size_t elen = str->read2();
        e->name.resize(elen);
        str->readBytesInto((uint8_t*)&(e->name)[0], elen);

        return StatResult::readInto(str, &e->stat);
    }
};

#endif
