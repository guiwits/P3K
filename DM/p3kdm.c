#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <ctype.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/types.h>

#include "comm.h"
#include "genIII_if.h"

char device[128] = "192.168.0.100";
int baud_rate    = 115200;

int send_data (driver_t driver);

int main (int argc, char *argv[])
{
	FILE *ifp = NULL;
	int i = 0;
	int d = 0;
	size_t bytes_read;
	float dm_data[DATA_SIZE];	/* 3840 */
	driver_t driver[8];
	int up = FALSE;
	int clear = FALSE;
	int down = FALSE;
	int query = FALSE;
	int status = FALSE;
	float bias = 0.0;			/* 0.0 - 70.0 volts */
	int fd;
	int failed = 0;
	int length;
	char *qfn = NULL;		/* file to put query results in */	
	char *mode = NULL;		/* normal or test */
	
	/*
	 * -d Put the DM in inactive mode (e.g. before DM power-off)
	 * -b is to set the bias on the drivers
	 * -c clears faults on each driver
	 * -f is the filename to read the command or frame from
	 * -p is the device to write to (/dev/ttyS0 is the default)
	 * -q query the current DM voltages. If filename present, write to file otherwise to standard out
	 * -s return the status of the DM
	 * -u put the DM in power-on/active mode. Run only once after DM power-on
	 */
	
	if (argc < 2) {
		(void) fprintf (stderr, "Usage: p3kdm -f filename [-b bias] [-c]"
					"[-d] [-m mode] [-q <filename>] [-s] [-u] \n");
		return EXIT_FAILURE;
	}
	
	for (i = 1; i < argc; i++) {
		if ((strcmp(argv[i], "-p") == 0)
			&& (argv[i + 1] != NULL)) {
			strncpy(device, argv[++i], sizeof(device));
		} else if ((strcmp(argv[i], "-f") == 0)
				   && (argv[i + 1] != NULL)) {
			if ((ifp = fopen (argv[++i], "r")) == NULL) {
				printf ("Error: can't open %s\n", argv[i]);
				return EXIT_FAILURE;
			}
		} else if ((strcmp (argv[i], "-d") == 0)) {
			down = TRUE;
		} else if ((strcmp (argv[i], "-b") == 0)) {
			if (argv[i+1] != NULL) bias = atof (argv[++i]);
		} else if ((strcmp (argv[i], "-u") == 0)) {
			up = TRUE;
		} else if ((strcmp (argv[i], "-c") == 0)) {
			clear = TRUE;
		} else if ((strcmp (argv[i], "-m") == 0)) {
			if ((argv[i + 1] != NULL)) {
				up = TRUE;
			 	mode = malloc (strlen (argv[i+1]));
			 	strncpy (mode, argv[i+1], strlen (argv[i+1]));
				i = i + 1;

				if ((strcasecmp (mode, "normal") == 0) || (strcasecmp (mode, "test") == 0)) {
					//printf ("setting mode to %s mode.\n", mode);
				} else {
					printf ("ERROR: mode must either be test or normal.\n");
					exit (-1);
				}
			}
		} else if ((strcmp (argv[i], "-q") == 0)) {
			query = TRUE;
			if ((argv[i + 1] != NULL) && (strlen (argv[i + 1]) > 3)) {
			 	qfn = malloc (strlen (argv[i+1]));
			 	strncpy (qfn, argv[i+1], strlen (argv[i+1]));
				i = i + 1;
			}
		} else if ((strcmp (argv[i], "-s") == 0)) {
			status = TRUE;
		} else {
			(void) fprintf(stderr, "Usage: p3kdm [-f filename] [-b bias] [-c] "
						"[-d] [-n] [-q <filename>] [-s] [-t] [-u]\n");
			return EXIT_FAILURE;
		}
	}

	// Set up the port communications for each driver //
	//printf ("Setting up the communications with DM Drivers.\n");
	for (i = 0; i < NUM_DRIVERS; i++)
	{
		int port = 10000 + i;
		if ((driver[i].fd = open_comm (device, port)) < 0) 
		{
			printf ("Error: driver %d: Cannot open device communication port\n", i);
			failed = failed + 1;
		}
		
	}
	//printf ("DM Drivers communication settup complete.\n");

	if (failed > 0) { 
                printf ("%d driver(s) failed to intialize communucations. Exiting ...\n", failed); 
		failed = 0;
                exit (-1);
	}

	if (mode != NULL) {
	 	/* Setting the mode of the DM Drivers */
		printf ("Setting the DM Driver modes.\n");
		if (dm_mode (driver, mode) != 0) {
			printf ("ERROR: Failed setting the DM Mode.\n");
			exit (-1);
		}
		printf ("dm_mode completed successfully.\n");
	}

	/* Bring the drivers up */
	if (up == 1) {
                /* Turn on the driver */
		printf ("Bringing the DM Drivers up.\n");
                if (dm_up (driver[0].fd) == 0) {
                        printf ("dm_up completed successfully.\n");
                } else {
			printf ("dm_up did not complete successfully.\n");
			exit (-1);
		}
        }
        
        if (down == 1) {
                /* Turn off the driver */
		printf ("Bringing the DM Drivers down.\n");
                if (dm_down (driver[0].fd) == 0) {
                        printf ("dm_down completed successfully.\n");
                } else {
			printf ("dm_down did not complete successfully.\n");
			exit (-1);
		}
        }

	if (clear == 1) {
		//printf ("Clearing DM Drivers. (%d).\n", NUM_DRIVERS);
		for (i = 0; i < NUM_DRIVERS; i++) {
            if (dm_clear (driver[i].fd) == 0) {
                //printf ("Driver %d cleared successfully.\n", i);
            } else {
				printf ("Driver %d did not clear successfully.\n", i);
				exit (-1);
			}
		}
	}

	if (status == 1) {
		/* Get the status of the driver */
		for (i = 0; i < NUM_DRIVERS; i++) {
			if ((dm_status (driver[i].fd, i)) == 0) {
				printf ("dm_status for driver %i completed successfully.\n", i); 
				fflush (stdout);
			} else {
				printf ("dm_status for driver %i did not execute properly.\n", i);
				exit (-1);
			}
		}
	}
#if 0	
	
	if (query == 1) {
		/* Query the voltage values of the driver */
		if ((dm_query (qfn, fd) == 0)) {
			printf ("dm_query completed successfully.\n");
		} else {
			printf ("dm_query did not execute properly.\n");
		}
		
	}
#endif

	
	/***** format frame data and send it to driver(s) *****/
	if (ifp != NULL) {
			
		i = 0;
		d = 0;

		/* clear (mute) the drivers just for safety */
		for (i = 0; i < NUM_DRIVERS; i++) {
			if (dm_clear (driver[i].fd) == 0) {
				//printf ("Driver %d cleared successfully.\n", i);
			} else {
				printf ("Driver %d did not clear successfully.\n", i);
				exit (-1);
			}
		}

		/* read in data */
		i = 0;
		memset (dm_data, 0, sizeof (dm_data));
		while (fscanf (ifp, "%f", &dm_data[i]) != EOF) {
			//printf ("fscanf debug: data[%d] = %f\n", i, dm_data[i]);
			i++;
		}

		// Check to make sure values are within the allowed ranges
		limit_check (dm_data);
		//printf ("Successfully checked voltage limits\n");
		
		// Check that the neighbors of each actuator is within a certain range of one another 
		if ((interactuator_check (dm_data)) < 0) {
			printf ("ERROR: Interactuator limit failure occured. Exiting program.\n");
			exit (-1);
		}
		//printf ("Successfully checked interactuator limits\n");
		
		for (i = 0; i < NUM_DRIVERS; i++)
		{
			// Split up data into 8 different arrays and then convert and format it //
			// Copy driver[i] data over from DM data //
			split_data (dm_data, &driver[i], i);
			// Convert raw data to hex for formatting //
			for (d = 0; d < FRAME_SIZE; d++) {
				driver[i].data[d] = volts_to_counts (driver[i].raw_data[d]);
				//printf ("driver[%d].raw_data[%d] = %f\n", i, d, driver[i].raw_data[d]);
			}
			// Format the frame so the low end is sent first, then the high end
			format_data (&driver[i]);		
		}

		for (i = 0; i < NUM_DRIVERS; i++)
		{
			if (send_data (driver[i]) != 0) {
				printf ("Driver %d data encountered an error sending data.\n", i);
			} else {
				//printf ("Driver %d data sent successfully.\n", i);
			}
		}

		/* Unmute drivers */
		printf ("File written, bringing up the drivers.\n");
                if (dm_up (driver[0].fd) == 0) {
                        printf ("dm_up completed successfully.\n");
                } else {
                        printf ("dm_up did not complete successfully.\n");
                        exit (-1);
                }

	}


	/* Set Bias Check */
	if (bias > 0.0) {
		
#if 0
		/* mute the drivers */
		for (i = 0; i < NUM_DRIVERS; i++) {
			if (dm_clear (driver[i].fd) == 0) {
				//printf ("Driver %d cleared successfully.\n", i);
			} else {
				printf ("Driver %d did not clear successfully.\n", i);
				exit (-1);
			}
	    }
		
		// We won't set the mode. Leave it in what ever mode they are currently in.
		printf ("putting the drivers in normal mode.\n");
		if (dm_mode (driver, mode) != 0) {
			printf ("ERROR: Failed setting the DM Mode.\n");
		}
		
		up = FALSE;
#endif
		
		// Drivers MUST be up before bias is set.
		// NOTE: Another "up" command after setting bias will reset bias to default.
		
		/* Turn on the driver */
		//printf ("Bringing the DM Drivers up.\n");
		if (dm_up (driver[0].fd) == 0) {
			//printf ("dm_up completed successfully.\n");
		} else {
			printf ("dm_up did not complete successfully.\n");
			exit (-1);
		}
		
		if ((dm_set_bias (driver, bias)) != 0) {
			printf ("ERROR: Failed to return from the set bias function.\n");
		}
	}

	/* close our file desc. and file pointer */
	if (ifp != NULL) 
	{
	  fclose (ifp);
	}

	//printf ("Closing communication links.\n");
	for (i = 0; i < NUM_DRIVERS; i++) 
	{
		close (driver[i].fd);
	}
	
	return EXIT_SUCCESS;
}

int send_data (driver_t driver) {

	struct timeval timeout;
	unsigned char read_buffer[8192];
	unsigned char response[8192];
	fd_set readfs;
	int recv_len;
	int resp_len;
	int status;


//#if 0
	if (driver.volts == NULL) {
	   printf ("Error: send_data: volts is NULL\n");
           errno = EINVAL;
           return ERROR;
	}
	
	if (strlen ((char *) driver.volts) == 0)  {
           printf ("Error: send_data: volts is empty string\n");
           errno = EINVAL;
           return ERROR;
        }

	memset (driver.resp, 0, sizeof (driver.resp));
	FD_ZERO (&readfs);
	FD_SET (driver.fd, &readfs);
	
	if (write (driver.fd, driver.volts, (sizeof (driver.volts))) < 0) { 
		printf ("Error: send_data: %s\n", strerror (errno)); 
		return (EXIT_FAILURE); 
	}

 	recv_len = 0; 
	memset (response, 0, sizeof (response));

 	for (;;) { 
		int len;

 		/* Wait 1 second for a response. This may seem long, but certain */ 
		/* commands (e.g. internal tests) take this much time to respond. */
		timeout.tv_sec = 1; 
		timeout.tv_usec = 0;

 		/* Wait for a response */ 
		status = select (FD_SETSIZE, &readfs, (fd_set *) 0, (fd_set *) 0, &timeout);

 		/* Error in select () */ 
		if (status < 0) { 
			printf ("Error: send_data: %s\n", strerror (errno)); 
			return -1; 
		}

 		/* Timeout while waiting for a response */ 
		else if (status == 0) { 
			printf ("status = 0: Received: %s [length : %i]\n", response, recv_len); 
			break; 
		}

 		/* Don't overflow the response buffer. Instead, flush the port */ 
		/* and return an error */ 
		if (recv_len >= sizeof (response)) { 
			printf ("Internal Error: send_data: response buffer too small for data received\n"); 
			errno = EINVAL; 
			return -1; 
		}

 		/* Read the response */ 
		if ((len = read (driver.fd, read_buffer, sizeof (response) - recv_len)) < 0) { 
			printf ("Error: send_data: %s\n", strerror (errno)); 
			return -1; 
		}

 		/* Append the response to the end of the response buffer */ 
		memcpy (response + recv_len, read_buffer, len); 
		recv_len += len; 

		if (response[0] == '>') { 
			break;
		} else if (recv_len >= 962) {
			break;
		}
	}
	
	/*
	 If the caller has requested the response, copy the response into the
	 caller-provided buffer, making sure not to overflow.
	 Then NULL-terminate the response.
        */
	
    if (driver.resp != NULL)  {
        //printf ("Received: [length : %i] -- Response = %s\n", recv_len, response);

        if (resp_len >= recv_len)  {
            memcpy (driver.resp, response, recv_len);
        }
        else  {
            memcpy (driver.resp, response, resp_len);
        }
    }

//#endif

    errno = 0;

	return 0;
}




