#ifndef H_INDEX
#define H_INDEX

#include <vector>
#include <map>

#include "packet.h"
#include "mem_stream.h"

class BundleIndex
{
public:
    typedef std::vector<IndexEntry> Entries;
private:
    // map from group name (e.g. dir, tag, etc.) to filenames
    typedef std::map<std::string, Entries> GroupMap;
    GroupMap mGroupToFiles;

    bool mLoaded;

public:
    bool getLoaded() const { return mLoaded; }
    const Entries &getList(const std::string &group) { return mGroupToFiles[group]; }

    void readFromPacket(Header *h, mem_stream<true> *s);
};

class FsIndex
{
private:
    std::vector<std::string> mBundles;
};

#endif
