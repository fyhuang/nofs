#include "nofs_fuse.h"
#include "index.h"

void BundleIndex::readFromPacket(Header *h, mem_stream<true> *ms)
{
    size_t num_entries = ms->read4();
    for (size_t i = 0; i < num_entries; i++) {
        IndexEntry ie;
        IndexEntry::readInto(ms, &ie);

        DBPRINTF("Reading index entry\n");
        
        const char *iename = ie.name.c_str();
        const char *fname_c = strrchr(iename, '/') + 1;
        std::string filename = fname_c;
        std::string dirname = ie.name.c_str()+1;
        dirname.resize(fname_c - iename - 1);
        if (dirname.size() > 0) {
            // If dirname != "", strip trailing slash
            dirname.resize(dirname.size() - 1);
        }
        ie.name = filename;

        DBPRINTF("Parsed: dirname '%s' filename '%s'\n", dirname.c_str(), filename.c_str());

        GroupMap::iterator it_e = mGroupToFiles.find(dirname);
        if (it_e == mGroupToFiles.end()) {
            it_e = mGroupToFiles.insert(std::make_pair(dirname, Entries())).first;
        }

        Entries &ent = (*it_e).second;
        ent.push_back(ie);
    }

    mLoaded = true;
    DBPRINTF("Finished loading index\n");
}
