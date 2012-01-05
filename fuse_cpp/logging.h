#ifndef H_LOGGING
#define H_LOGGING

#ifdef DEBUG
#define DBPRINTF(...) debug_printf(__VA_ARGS__)
#define DBERROR(errcode) DBPRINTF("%s returning %d\n", __func__, errcode); return -errcode
#else
#define DBPRINTF(...) do{}while(false)
#endif

extern void debug_printf(const char *format, ...);
extern void logerror_real(const char *what, const char *func, int line);

#define logerror(what) logerror_real(what, __func__, __LINE__)

#endif
