#ifndef COMM_H
#define COMM_H

#ifndef FALSE
#define FALSE   0
#endif

#ifndef TRUE
#define TRUE    1
#endif

#ifndef ERROR
#define ERROR   (-1)
#endif

#ifndef SUCCESS
#define SUCCESS 0
#endif

#ifndef OFF
#define OFF     0
#endif

#ifndef ON
#define ON      1
#endif

#ifndef NULL
#define NULL    0
#endif

#ifndef NULLP
#define NULLP   (char *)0
#endif

extern int open_comm (const char *addr, int arg);
extern int send_raw (int fd, char *text, char *resp, int resp_len);

#endif              /* COMM_H */
