#ifndef UTIL_H
#define UTIL_H

extern int open_comm (char *addr, int arg);
extern int send_raw (int fd, char *text, char *resp, int resp_len);

#endif              /* UTIL_H */
