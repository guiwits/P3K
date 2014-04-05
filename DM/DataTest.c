#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <ctype.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/types.h>

#include "dm_if.h"


int main (int argc, char **argv)
{
    FILE *ifp;
    int i = 0;
    unsigned char text[962];
    size_t bytes_read;
    frame_t frame;
    float voltage_data[96];

    if ((ifp = fopen (argv[1], "r")) == NULL) {
	return EXIT_FAILURE;
    }

	bzero (text, sizeof (text));
	
    /* read data */
    bytes_read = fread (&frame.id, sizeof (frame.id), 1, ifp);
    bytes_read = fread (&frame.dt, sizeof (frame.dt), 1, ifp);
	
	while (fscanf (ifp, "%f", &frame.raw_data[i]) != EOF) {
		printf ("fscanf debug (volts read in): data[%d] = %f\n", i, frame.raw_data[i]);
		i++;
    }

	//limit_check (frame.raw_data);
	
	//for (i = 0; i < FRAME_SIZE; i++)
	for (i = 0; i < 97; i++)
	{
		frame.data[i] = volts_to_counts (frame.raw_data[i]);
		//printf ("frame.data[%d] = %x\n", i, frame.data[i]);
		printf ("frame.data[%d] = 0x%x (%d)\n", i, frame.data[i], frame.data[i]);
	}
	
	printf ("\n\n Now going back to volts \n\n");
	//for (i = 0; i < FRAME_SIZE; i++)
	for (i = 0; i < 97; i++)
	{
		voltage_data[i] = counts_to_volts (frame.data[i]);
		printf ("voltage_data[%d] = %f\n", i, voltage_data[i]);
	}
	
	/*
	printf ("FORMATTING FRAME\n");
	format_frame (frame, text, sizeof (text));

	printf ("text = %x %x\n", text[0], text[1]);
	for (i = 0; i < sizeof (text); i++)
	{
		printf ("%d 0x%.02x\n", i, text[i]);
	}
	 */

	
    return EXIT_SUCCESS;
}
