#ifndef H_LOGGING
#define H_LOGGING

#ifdef DEBUG
#define DBPRINTF(...) _debug_printf(__func__, __LINE__, __VA_ARGS__)
#define DBERROR(errcode) DBPRINTF("%s returning %d\n", __func__, errcode); return -errcode
#else
#define DBPRINTF(...) do{}while(false)
#endif

extern void _debug_printf(const char *format, ...);
extern void _syslog_error(const char *what, const char *func, int *line);

#define LOGERROR(x) _syslog_error(x, __func__, __LINE__)

#endif
