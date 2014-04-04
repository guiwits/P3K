#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <ctype.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/types.h>

#include "comm.h"
#include "dm_if.h"

char	device[128] = "/dev/ttyS0";
int		baud_rate = 115200;

static int send_to_serial (int fd, char *text, char *resp, int resp_len);

int main (int argc, char *argv[])
{
	FILE *ifp;
	int i = 0;
	size_t bytes_read;
	frame_t frame;
	command_t command;
	char text[4096];
	char resp[4096];
	char *type = frame;
	int fd;
	int length;
	fd_set readfs;
	struct timeval timeout;
	char read_buffer[4096];
	char response[4096];
	int recv_len;
	int status;
	
	
	/*
	 * -d is the device to write to (/dev/ttyS0 is the default)
	 * -b is the baud rate to communicate at (115200 is the default)
	 * -c tell the program that a command is being issues rather than writing a frame
	 * -f is the filename to read the command or frame from
	 */
	if (argc < 3) {
		(void) fprintf (stderr, "Usage: dm_send [-d device] [-b baudrate] [-c] -f filename\n");
		return EXIT_FAILURE;
	}
	
	for (i = 1; i < argc; i++) {
		if ((strcmp(argv[i], "-d") == 0)
			&& (argv[i + 1] != NULL)) {
			strncpy(device, argv[++i], sizeof(device));
		} else if ((strcmp(argv[i], "-b") == 0)
				   && (argv[i + 1] != NULL)) {
			baud_rate = atoi (argv[++i]);
		} else if ((strcmp(argv[i], "-f") == 0)
				   && (argv[i + 1] != NULL)) {
			if ((ifp = fopen (argv[++i], "r")) == NULL) {
				printf ("Error: can't open %s\n", argv[i]);
				return EXIT_FAILURE;
			}
		} else if ((strcmp(argv[i], "-c") == 0)) {
			type = command;
		} else {
			(void) fprintf(stderr,
						   "Usage: dm_send [-d device] [-b baudrate] [-c]  -f filename\n");
			return EXIT_FAILURE;
		}
	}
	
	/* open the serial port and set up the buad rate */
	if ((fd = open_comm (device, baud_rate)) < 0) {
		fprintf (stderr, "Error: dm_send: Cannot open device %s: %s\n",
				 device, strerror (errno));
		return EXIT_FAILURE;
	}
	
	memset (resp, 0, sizeof (resp));
	FD_ZERO (&readfs);
	FD_SET (fd, &readfs);
	
	/* Determing if the type of data to write is a frame or a command */
	if (strcmp (type, "frame") == 0) {
		length = 55;
		
		/* read in data */
		bytes_read = fread (&frame.id, sizeof (frame.id), 1, ifp);
		bytes_read = fread (&frame.dt, sizeof (frame.dt), 1, ifp);
		while (fscanf (ifp, "%X", &frame.data[i]) != EOF) {
			printf ("debug: data[%d] = %X\n", i, frame.data[i]);
			i++;
		}
		
		//printf ("debug: command  length is %d\n", length);
		//format_frame (frame, text, sizeof (text));
		
		/* send the data  */
		if (write (fd, text, 57) < 0) {
			printf ("Error: send_raw: %s\n", strerror (errno));
			return -1;
		}
		
		print_frame (length, frame);
		
		recv_len = 0;
		memset (response, 0, sizeof (response));
		
		for (;;) {
			int len;
			
			/* Wait 1 second for a response. This may seem long, but certain   */
			/* commands (e.g. internal tests) take this much time to respond. */
			
			timeout.tv_sec = 1;
			timeout.tv_usec = 0;
			
			/* Wait for a response */
			status =
			select (FD_SETSIZE, &readfs, (fd_set *) 0, (fd_set *) 0,
					&timeout);
			
			/* Error in select () */
			if (status < 0) {
				printf ("Error: send_raw: %s\n", strerror (errno));
				return -1;
			}
			
			/* Timeout while waiting for a response */
			else if (status == 0) {
				printf ("Received: %s [length : %i]\n", response,
						recv_len);
				break;
			}
			
			/* Don't overflow the response buffer. Instead, flush the port */
			/* and return an error */
			if (recv_len >= sizeof (response)) {
				printf
				("Internal Error: send_raw: response buffer too small for "
				 "data received\n");
				errno = EINVAL;
				return -1;
			}
			
			/* Read the response */
			if ((len =
				 read (fd, read_buffer,
					   sizeof (response) - recv_len)) < 0) {
				printf ("Error: send_raw: %s\n", strerror (errno));
				return -1;
			}
			
			/* Append the response to the end of the response buffer */
			memcpy (response + recv_len, read_buffer, len);
			recv_len += len;
		}
	}
	else {
		length = 1;
		
		/* read in data */
		bytes_read = fread (&command.id, sizeof (command.id), 1, ifp);
		while (fscanf (ifp, "%X", &command.data[i]) != EOF) {
			printf ("debug: data[%d] = %X\n", i, command.data[i]);
			i++;
		}
		
		printf ("debug: command  length is %d\n", length);
		format_command (command, text, sizeof (text));
		
		/* send the data  */
		if (write (fd, text, 3) < 0) {
			printf ("Error: send_raw: %s\n", strerror (errno));
			return -1;
		}
		
		recv_len = 0;
		memset (response, 0, sizeof (response));
		
		for (;;) {
			int len;
			
			/* Wait 5 seconds for a response. This may seem long, but certain   */
			/* commands (e.g. internal tests) take this much time to respond. */
			
			timeout.tv_sec = 1;
			timeout.tv_usec = 0;
			
			/* Wait for a response */
			status = select (FD_SETSIZE, &readfs, (fd_set *) 0, (fd_set *) 0,
					         &timeout);
			
			/* Error in select () */
			if (status < 0) {
				printf ("Error: send_raw: %s\n", strerror (errno));
				return -1;
			}
			
			/* Timeout while waiting for a response */
			else if (status == 0) {
				printf ("Received: %s [length : %i]\n", response,
						recv_len);
				break;
			}
			
			/* Don't overflow the response buffer. Instead, flush the port */
			/* and return an error */
			if (recv_len >= sizeof (response)) {
				printf
				("Internal Error: send_raw: response buffer too small for "
				 "data received\n");
				errno = EINVAL;
				return -1;
			}
			
			/* Read the response */
			if ((len =
				 read (fd, read_buffer,
					   sizeof (response) - recv_len)) < 0) {
				printf ("Error: send_raw: %s\n", strerror (errno));
				return -1;
			}
			
			/* Append the response to the end of the response buffer */
			memcpy (response + recv_len, read_buffer, len);
			recv_len += len;
		}
		
		printf ("%s responded with %s\n", device, resp);
	}
	
	
	/* close our file desc. and file pointer */
	fclose (ifp);
	close (fd);
	
	return EXIT_SUCCESS;
}
