#include <stdio.h>
#include <stdlib.h>
#include <strings.h>

#include "dm_if.h"


void print_frame (int length, frame_t frame)
{
	
	int i = 0;
	
	/* print out data */
	printf ("\nData read from file\n--------------\n");
	printf ("id: %X\n", frame.id);
	printf ("data type: %X\n", frame.dt);
	
	for (i = 0; i < length; i++) {
		printf ("data[%d]: %X\n", i, frame.data[i]);
	}
	printf ("\n");
	
	return;
}

void print_command (int length, command_t command)
{
	int i = 0;
	
	/* print out data */
	printf ("\nData read from file\n--------------\n");
	printf ("id: %X\n", command.id);
	
	for (i = 0; i < length; i++) {
		printf ("data[%d]: %X\n", i, command.data[i]);
	}
	printf ("\n");
	
	return;
}

void format_command (command_t command, char *text, int len)
{
	int i = 0;
	short tmp;
	
	/* clean the text buffer */
	bzero (text, len);
	
	text[0] = command.id;
	
	tmp = command.data[0] >> 8;
	text[2] = (char) (tmp & 0xFF);0
	text[1] = (char) (command.data[0] & 0xFF); 
	
	printf ("text = %.02X %.02X %.02X\n", text[0] & 0xFF, text[1] & 0xFF, text[2] & 0xFF);
	
	return; 
}

/* ----------------------------------------------------------*/
void format_frame (frame_t frame, char *text, int len)
{
	int i = 0;
	short tmp;
	
	/* clean the text buffer */
	bzero (text, len);
	
	text[0] = frame.id;
	text[1] = frame.dt;
	
	/* i + 2 and i + 3 have to do with the fact that the first two array elements
	 * are taken by the frame id and dt, which are each character elements.
	 */
	for (i = 0; i < FRAME_SIZE; i++)
	{
		tmp = frame.data[i] >> 8;
		text[i + 2] = (char) (frame.data[i] & 0xFF); 
		text[i + 3] = (char) (tmp & 0xFF);
	}
	
	printf ("text = %.02X %.02X ", text[0] & 0xFF, text[1] & 0xFF);
	for (i = 2; i < FRAME_SIZE; i++)
	{
		printf ("%.02X ", text[i] & 0xFF);		
	}
	printf ("\n");
	
	return; 
}
