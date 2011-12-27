#include "nofs_fuse.h"

THREAD_LOCAL char g_Bundle[4096];
THREAD_LOCAL char g_Path[4096];

bool nofs_splitpath(const char *input, char **bundle, char **path) {
    syslog(LOG_ERR, "nofs_splitpath %s", input);

    const char *after_bundle = strchr(input + 1, '/');
    size_t path_len = 0;
    size_t bsize = 0;
    if (after_bundle != NULL) {
        path_len = strlen(after_bundle + 1);
        bsize = after_bundle - input - 1;
    }
    else {
        bsize = strlen(input+1);
    }

    if (path_len > 0) {
        memcpy(&g_Path[0], after_bundle+1, path_len);
        g_Path[path_len] = '\0';
        *path = g_Path;

        memcpy(&g_Bundle[0], input + 1, bsize);
        g_Bundle[bsize] = '\0';
        *bundle = g_Bundle;
        return true;
    }
    else {
        *path = NULL;
        memcpy(&g_Bundle[0], input + 1, bsize);
        g_Bundle[bsize] = '\0';
        *bundle = g_Bundle;
        return false;
    }
}

