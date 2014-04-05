#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <termios.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/time.h>

#include "ao.h"
#include "comm.h"

static int parse_inet_addr (const char *addr);
extern int setup_inet (const char *inet_addr, int port);
static int setup_serial (const char *device_name, int baud_rate);
static int get_baud_posix (int baud_rate);

int open_comm (const char *addr, int arg)
{
    int port;
    int baud_rate;
    int fd;
    
    port = arg;
    baud_rate = arg;

    //printf ("open_comm: %s %d\n", addr, arg);
    
    if (parse_inet_addr (addr) == TRUE)  {
        if ((fd = setup_inet (addr, port)) == ERROR)  {
            printf ("Error: open_comm: Invalid address %s:%d\n", addr, port);
            return ERROR;
        }
    }
    else  {
        if ((fd = setup_serial (addr, baud_rate)) == ERROR)  {
            printf ("Error: open_comm: Invalid address %s\n", addr);
            return ERROR;
        }
    }    
    return fd;
}


#ifdef FUNCT_HDR
/* ***************************************************************************
*
*  Synopsis:
*       int parse_inet_addr (const char *addr, int *port);
*
*  Description:  
*       parse_inet_addr () will look at the first character of "addr"
*       If it is a '/', the function assumes it refers to a serial device;
*       otherwise, the function assumes it is an internet address.
*
*  Return Values:
*       TRUE    If the address is an internet address
*       FALSE   Otherwise
*
*  Notes:
*       Obviously, there are many possible inputs that are neither serial
*       devices nor internet addresses. This function makes absolutely no
*       effort to identify these.
*
*****************************************************************************/
#endif

int parse_inet_addr (const char *addr)
{
    if (addr == NULL)  {
        printf ("Error: parse_inet_addr: NULL addr\n");
        return FALSE;
    }
    if (addr[0] == '/')  {
        return FALSE;
    }

    return TRUE;
}

int setup_inet (const char *addr, int port)
{
    struct sockaddr_in server_addr;
    int fd;

    if (addr == NULL)  {
        printf ("Error: setup_inet: NULL addr\n");
        errno = EINVAL;
        return ERROR;
    }
    bzero (&server_addr, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = inet_addr (addr);  
    server_addr.sin_port = htons (port);
    
    if ((fd = socket (AF_INET, SOCK_STREAM, 0)) == -1)  {
        printf ("Error: setup_inet: socket: %s\n", strerror (errno)); 
        return ERROR;
    } 
    
    if (connect (fd, (struct sockaddr *) &server_addr, sizeof (server_addr)) == -1)  { 
        printf ("Error: setup_inet: connect: %s\n", strerror (errno));
        close (fd);          
        return ERROR;
    } 

    return fd;
}


int setup_serial (const char *device_name, int baud_rate)
{
    struct termios attr;
    int baud_posix;
    int fd;

    if (device_name == NULL)  {
        printf ("Error: setup_serial: NULL device_name\n");
        errno = EINVAL;
        return ERROR;
    }

    if ((fd = open (device_name, O_RDWR, 0)) < 0)  {
        printf ("Error: setup_serial: open: %s\n", strerror (errno));
        return ERROR;
    }

/*
 Get the current terminal parameters
 */
    if (tcgetattr (fd, &attr) != 0)  {
        printf ("Error: mm2000_setup_posix: Unable to get terminal "
                "attributes\n");
        return -1;
    }
    
    attr.c_iflag &= ~(BRKINT |          /* Ignore break */
                      IGNPAR |          /* Ignore parity */
                      PARMRK |          /* Ignore parity */
                      INPCK |           /* Ignore parity */
                      ISTRIP |          /* Don't strip to 7 bits */
                      INLCR |           /* Don't process <lf> or <cr> */
                      IGNCR |           /* Don't process <lf> or <cr> */
                      ICRNL |           /* Don't process <lf> or <cr> */
                      IXON |            /* Don't use XON/XOFF */
                      IXOFF);           /* Don't use XON/XOFF */
    attr.c_iflag |= IGNBRK;             /* Don't generate SIGINT on break */
    
    attr.c_oflag &= ~(OPOST);

    attr.c_lflag &= ~(ECHO |
                      ECHOE |
                      ECHOK |
                      ECHONL |
                      ICANON |
                      ISIG |
                      NOFLSH |
                      TOSTOP);

    /* Set control parameters */
    attr.c_cflag &= ~CSIZE;             /* Clear data bit field */
    attr.c_cflag |= CLOCAL |            /* Ignore modem status lines */
                    CREAD |             /* Enable receiving characters */
                    CS8;                /* 8 Data Bits */
    attr.c_cflag &= ~(CSTOPB |          /* 1 Stop Bit */
                     PARENB);           /* No Parity */
  
    /* Set Baud Rate */
    if ((baud_posix = get_baud_posix (baud_rate)) == ERROR)  {
        printf ("Error: setup_serial: Invalid baud rate %d\n", baud_rate);
        close (fd);
        return ERROR;
    }
    if (cfsetispeed (&attr, baud_posix) != 0)  {
        printf ("Error: setup_posix: Unable to set baud rate\n");
        return -1;
    }
    if (cfsetospeed (&attr, baud_posix) != 0)  {
        printf ("Error: setup_posix: Unable to set baud rate\n");
        return -1;
    }
    
    /* Flush input data */
    if (tcflush (fd, TCIFLUSH) != 0)  {
        printf ("Error: setup_posix: Unable to flush input data\n");
        return -1;
    }
    
    if (tcsetattr (fd, TCSAFLUSH, &attr) != 0)  {
        printf ("Error: setup_posix: Unable to set terminal attributes\n");
        return -1;
    }

    return fd;
}

int get_baud_posix (int baud_rate)
{
    int baud_posix;
    
    switch (baud_rate)  {
        case 9600:
            baud_posix = B9600;
            break;
        case 19200:
            baud_posix = B19200;
            break;
        case 38400:
            baud_posix = B38400;
            break;
        default:
            baud_posix = ERROR;
            break;
    }
    return baud_posix;
}


extern int send_raw (int fd, char *text, char *resp, int resp_len)
{
    fd_set readfs;
    struct timeval timeout;
    char read_buffer[1024];
    char response[1024];
    int recv_len;
    int status;
    
    if (text == NULL)  {
        printf ("Error: send_raw: text is NULL\n");
        errno = EINVAL;
        return ERROR;
    }
    if (strlen (text) == 0)  {
        printf ("Error: send_raw: text is empty string\n");
        errno = EINVAL;
        return ERROR;
    }
    
    FD_ZERO (&readfs);
    FD_SET (fd, &readfs);
    
    /* Send the text */ 
    if (write (fd, text, strlen (text)) < 0)  {
        printf ("Error: send_raw: %s\n", strerror (errno));
        return ERROR;
    }
    
    //printf ("sent %s \n", text);
    //printf("size text %d \n", (int) strlen(text));
#if 1
   
    /* Wait for the device to respond */
    recv_len = 0;
    memset (response, 0, sizeof (response));
    for (;;)  {
        int len;

        /* Wait 2 seconds for a response. This may seem long, but certain   */
        /* commands (e.g. resetting limits) take this much time to respond. */

        timeout.tv_sec  = 2;
        timeout.tv_usec = 0;    
	
        /* Wait for a response */
        status = select (FD_SETSIZE, &readfs, (fd_set *)0, (fd_set *)0, &timeout);
	//printf ("time left on select = %ld.%ld\n", timeout.tv_sec, timeout.tv_usec);

        /* Error in select () */
        if (status < 0)  {
            printf ("Error: send_raw: %s\n", strerror (errno));
            return ERROR;
        }

        /* Timeout while waiting for a response */
        else if (status == 0)  {
            //printf ("send_raw: Timeout while attempting to read response\n");
            break;
        }

        /* Don't overflow the response buffer. Instead, flush the port */
        /* and return an error */
        if (recv_len >= sizeof (response))  {
            printf ("Internal Error: send_raw: response buffer too small for data received\n");
            errno = EINVAL;
            return ERROR;
        }

        /* Read the response */
        if ((len = 
             read (fd, read_buffer, sizeof (response) - recv_len)) < 0)  {
             printf ("Error: send_raw: %s\n", strerror (errno));
             return ERROR;
        }

        /* Append the response to the end of the response buffer */
        memcpy (response + recv_len, read_buffer, len);
        recv_len += len;

//	printf ("%s\n", response);

	if (response[0] == '>') {
		break;
	} else if (recv_len >= 962) {
		break;
	}
    }
    
    //printf ("received ", response, recv_len);
    /*
       If the caller has requested the response, copy the response into the
       caller-provided buffer, making sure not to overflow.
       Then NULL-terminate the response.
     */

    if (resp != NULL)  {
        if (resp_len >= recv_len)  {
            memcpy (resp, response, recv_len);
        }
        else  {
            memcpy (resp, response, resp_len);
        }
    }
#endif 
    errno = 0;
        
    return SUCCESS;

}

