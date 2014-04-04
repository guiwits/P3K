#ifndef DM_IF_H
#define DM_IF_H

#define FRAME_SIZE		1080
#define COMMAND_SIZE	1

typedef struct {
	char id;							/* id number      */
	char dt;							/* data type      */
	unsigned short data[FRAME_SIZE];	/* hex frame data */
} frame_t;

typedef struct {
	char id;							/* id number      */
	unsigned short data[COMMAND_SIZE];	/* hex frame data */
} command_t;

void print_frame (int lenght, frame_t frame);
void print_command (int lenght, command_t command);
void format_command (command_t command, char *text, int len);
void format_frame (frame_t frame, char *text, int len);

#endif		/* DM_IF_H */