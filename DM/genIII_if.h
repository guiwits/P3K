#ifndef GENIII_IF_H
#define GENIII_IF_H

#define DATA_SIZE	3840	/* size of entire data set ((48 channels * 10 cards) * 8 drivers) */
#define FRAME_SIZE 	480		/* Size of a single driver frame */
#define NUM_CARDS	10		/* number of cards in the GenIII driver	*/
#define NUM_DRIVERS 8
#define VMAX ((float) 30)
#define VMIN ((float) -30)
#define CMAX ((short) 32767)
#define CMIN ((short) -32768)

/* Port numbers for terminal server -> driver */
#define D0_PORT		10000
#define D1_PORT		10001
#define D2_PORT		10002
#define D3_PORT		10003
#define D4_PORT		10004
#define D5_PORT		10005
#define D6_PORT		10006
#define D7_PORT		10007

typedef struct { 
   int fd;							/* file desc. for terminal port	*/
   char id;							/* id number */
   char dt;							/* data type */
   signed short data[FRAME_SIZE];	/* hex frame data */
   float raw_data[FRAME_SIZE];		/* voltages from file */
   unsigned char volts[962];		/* character representation of data */
   unsigned char cbias[3];			/* character representation of bias data */
   unsigned char resp[8192];		/* response from the driver */
} driver_t;

int dm_up (int fd);
int dm_down (int fd);
int dm_clear (int fd);
int dm_set_bias (driver_t *driver, float bias);
int dm_status (int fd, int driver_number);
int dm_mode (driver_t *driver, char* mode);
int dm_query (char *qfn, int fd);
int limit_check (float *data);
int interactuator_check (float *data);
void print_data (driver_t frame);
void format_data (driver_t *driver);
void split_data (float dm_data[], driver_t *driver, int driver_num);
short volts_to_counts (float volts);
float counts_to_volts (signed short counts);

#endif		/* GENIII_IF_H */

