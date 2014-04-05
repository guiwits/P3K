#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

#include "comm.h"
#include "genIII_if.h"
#include "genIII_masks.h"

#define V_TBL_BYTES		96			/* Voltage bytes per card */ 
#define S_TBL_BYTES		28			/* Status bytes per card */
#define RAIL_CONV		19.2		/* Conversion factor for rail monitor */
#define VPP_CONV		20.0		/* Conversion factor for VPP */
#define V25_CONV		200.0		/* Conversion factor for 2.5 volts */
#define V33_CONV		200.0		/* Conversion factor for 3.3 volts */
#define VNN_CONV		-8.0		/* Conversion factor for VNN */
#define TS_CONV			7.0
#define NUM_ACTUATORS	3388		/* Number of actuators (11x11)			*/
#define NUM_ROWS		66	
#define NUM_COLS		66

int counter = 0;					/* Used for dm_clear since it has to try several times */

typedef struct {
	unsigned short stat;
	float ts1;
	float ts2;
	float ts3;
	float ts4;
	float ts5;
	float ts6;
	float ts7;
	float ts8;
	float vpp;
	float vnn;
	float bias;
	float v25;
	float v33;
} driver_status;

typedef struct {
	int board_16;   /* board 16 - board 11 are always 0          */
	int board_15;   /* board 16 - board 11 are always 0          */
	int board_14;   /* board 16 - board 11 are always 0          */
	int board_13;   /* board 16 - board 11 are always 0          */
	int board_12;   /* board 16 - board 11 are always 0          */
	int board_11;   /* board 16 - board 11 are always 0          */
	int board_10;   /* 1 if board 10 is responding to controller */
	int board_09;   /* 1 if board 09 is responding to controller */
	int board_08;   /* 1 if board 08 is responding to controller */
	int board_07;   /* 1 if board 07 is responding to controller */
	int board_06;   /* 1 if board 06 is responding to controller */
	int board_05;   /* 1 if board 05 is responding to controller */ 
	int board_04;   /* 1 if board 04 is responding to controller */
	int board_03;   /* 1 if board 03 is responding to controller */
	int board_02;   /* 1 if board 02 is responding to controller */ 
	int board_01;   /* 1 if board 01 is responding to controller */
} chassis_status;

typedef struct {
	int ready;
	int active;
	int ibactive;
	int testmode;
	int mfgmode;
	int hardmuted;
	int biasvalid;
	int error;
	int configerror;
	int powerfail;
	int biasfail;
	int overtemp;
	int driverfail;
	int fanfail;
	int nearrail;
	int slewratefail;
	chassis_status c_stat;
	float main_bias_volt;
	float aux_bias_volt;
	float volt_rail_mon;
	float backplane_temp;
	float fan_speeds;
	float dip_switches;
	driver_status ds[NUM_CARDS];
} controller_status;

typedef struct {
	char cmd;
	float v_table[NUM_CARDS * (V_TBL_BYTES / 2)];     /* data (short) */
} voltage_table;

int send_data_bias (driver_t driver);

static int format_status (controller_status *cs, const char *resp);

int limit_check (float *data)
{
	int i = 0;
	int max = 30;
	int min = -30;
	
	for (i = 0; i < DATA_SIZE; i++)
	{
		if ((data[i] < min) || (data[i] > max))
		{
			printf ("Data [%i] = %f\n", i, data[i]);
			printf ("Data exceeded Minimum/Maximum voltage.\n");
			exit (EXIT_FAILURE);
		}
	}
	
	return EXIT_SUCCESS;
}

int interactuator_check (float *data)
{
	/* Perform checking on actuator neighbors to make sure they aren't too far off 
     * voltage values from one another. */
	int i = 0;
	int j = 0;
	float diff_limit = 30.0;
	float volts[DMROWS][DMCOLS];
	int counter = 0;
	
	/* Fill the array with the 'data' in their correct locations */
	for (i = 0; i < 66; i++) 
	{
		for (j = 0; j < 66; j++)
		{
			//printf ("ActuatorMask Value is %d, i = %d, j = %d, counter is %d, ", ActuatorMask[i][j], i, j, counter);
			if (ActuatorMask[i][j] != 1)
			{
				volts[i][j] = data[counter];
				counter++;
				//printf (" -- Writing value %f\n", volts[i][j]);
			} else {
				volts[i][j] = 100.0;
				//printf (" -- Writing value %f\n", volts[i][j]);
			}	
		}
	}
		
	/* Now that the 2D array has the data we need, we can perform the inter-actuator checking */
	for (i = 0; i < NUM_ROWS; i++)
	{
		for (j = 0; j < NUM_COLS; j++)
		{
			
			/* if volt[i][j] is our known value, break out */
			if (volts[i][j] == 100.0) { 
				//printf ("volt[%d][%d] is our known value. Breaking out.\n", i, j);
				
			} else {
				
				if ((((i-1) >= 0) && ((i-1) < NUM_ROWS)) && (((j-1) >= 0) && ((j-1) < NUM_COLS)) 
					&& (volts[i-1][j-1] != 100.0)) {
					if (((abs ((1.0) * (volts[i][j] - volts[i-1][j-1])))) > diff_limit) {
						printf ("The difference between the voltages at volt[%d][%d] and volt[%d][%d] is > %.2f\n", 
						i, j, (i-1), (j-1), diff_limit);
						return -1;
					}
				} else {
					//printf ("index[%d][%d] is out of bounds.\n", (i-1), (j-1));
				}
				
				if ((((i-1) >= 0) && ((i-1) < NUM_ROWS)) && (((j) >= 0) && ((j) < NUM_COLS)) 
					&& (volts[i-1][j] != 100.0)) {
					if (((abs ((1.0) * (volts[i][j] - volts[i-1][j])))) > diff_limit) {
						printf ("The difference between the voltages at volt[%d][%d] and volt[%d][%d] is > %.2f\n", 
						i, j, (i-1), (j), diff_limit);
						return -1;
					}
				} else {
					//printf ("index[%d][%d] is out of bounds.\n", (i-1), (j));
				}
				
				if ((((i-1) >= 0) && ((i-1) < NUM_ROWS)) && (((j+1) >= 0) && ((j+1) < NUM_COLS)) 
					&& (volts[i-1][j+1] != 100.0)) {
					if (((abs ((1.0) * (volts[i][j] - volts[i-1][j+1])))) > diff_limit) {
						printf ("The difference between the voltages at volt[%d][%d] and volt[%d][%d] is > %.2f\n", 
								i, j, (i-1), (j+1), diff_limit);
						return -1;
					}
				} else {
					//printf ("index[%d][%d] is out of bounds.\n", (i-1), (j+1));
				}
				
				if ((( (i) >= 0) && ((i) < NUM_ROWS)) && (((j-1) >= 0) && ((j-1) < NUM_COLS)) 
					&& (volts[i][j-1] != 100.0)) {
					if (((abs ((1.0) * (volts[i][j] - volts[i][j-1])))) > diff_limit) {
						printf ("The difference between the voltages at volt[%d][%d] and volt[%d][%d] is > %.2f\n", 
						i, j, (i), (j-1), diff_limit);
						return -1;
					}
				} else {
					//printf ("index[%d][%d] is out of bounds.\n", (i), (j-1));
				}
				
				if ((((i) >= 0) && ((i) < NUM_ROWS)) && (((j+1) >= 0) && ((j+1) < NUM_COLS)) 
					&& (volts[i][j+1] != 100.0)) {
					if (((abs ((1.0) * (volts[i][j] - volts[i][j+1])))) > diff_limit) {
						printf ("The difference between the voltages at [%d][%d] and [%d][%d] is > %.2f\n", 
						i, j, (i), (j+1), diff_limit);
						return -1;
					}
				} else {
					//printf ("index[%d][%d] is out of bounds.\n", (i), (j+1));
				}
				
				if ((((i+1) >= 0) && ((i+1) < NUM_ROWS)) && (((j-1) >= 0) && ((j-1) < NUM_COLS)) 
					&& (volts[i+1][j-1] != 100.0)) {
					if (((abs ((1.0) * (volts[i][j] - volts[i+1][j-1])))) > diff_limit) {
						printf ("The difference between the voltages at volt[%d][%d] and volt[%d][%d] is > %.2f\n", 
						i, j, (i+1), (j-1), diff_limit);
						return -1;
					}
				} else {
					//printf ("index[%d][%d] is out of bounds.\n", (i+1), (j-1));
				}
				
				if ((((i+1) >= 0) && ((i+1) < NUM_ROWS)) && (((j) >= 0) && ((j) < NUM_COLS)) 
					&& (volts[i+1][j] != 100.0)) {
					if (((abs ((1.0) * (volts[i][j] - volts[i+1][j])))) > diff_limit) {
						printf ("The difference between the voltages at volt[%d][%d] and volt[%d][%d] is > %.2f\n", 
						i, j, (i+1), (j), diff_limit);
						return -1;
					}
				} else {
					//printf ("index[%d][%d] is out of bounds.\n", (i-1), (j-1));
				}
				
				if ((((i+1) >= 0) && ((i+1) < NUM_ROWS)) && (((j+1) >= 0) && ((j+1) < NUM_COLS)) 
					&& (volts[i+1][j+1] != 100.0)) {
					if (((abs ((1.0) * (volts[i][j] - volts[i+1][j+1])))) > diff_limit) {
						printf ("The difference between the voltages at volt[%d][%d] and volt[%d][%d] is > %.2f\n", 
						i, j, (i+1), (j+1), diff_limit);
						return -1;
					}
				} else {
					//printf ("index[%d][%d] is out of bounds.\n", (i+1), (j+1));
				}
			}
		}
	}
	
	return EXIT_SUCCESS;
}

int dm_up (int fd)
{
	char cmd[1024];
	char resp[1024];
	int i = 0;

	/* Send command (1) to put the set driver active  */
	strcpy (cmd, "1");
	memset (resp, 0, sizeof (resp));
	for (i = 0; i < 10; i++) { 
	   if ((send_raw (fd, cmd, resp, sizeof (resp)) != 0)) {
		   printf ("dm_up: failed to send command '1'.\n");
	   }
	
	   if (resp[0] != '>') {
		   printf ("dm_up received %s as a response.\n", resp);
		   printf ("dm_up did not receive the proper acknowledgement.\n");
		   if (i == 9) { 
		      printf ("Exiting after 10 tries.\n");
		   	  return EXIT_FAILURE;
           }
	   } else if (resp[0] == '>') {
		   //printf ("dm_up received %s as a response.\n", resp);
		   //printf ("dm_up received the proper acknowledgement.\n");
		   break;
	   }
	}

	return EXIT_SUCCESS;
}

int dm_down (int fd)
{
	char cmd[32];
	char resp[32];
	
	/* Send the command (0) to shut down the driver */
	strcpy (cmd, "0");
	memset (resp, 0, sizeof (resp));
	if ((send_raw (fd, cmd, resp, sizeof (resp)) != 0)) {
		printf ("dm_down: failed to send command '0'.\n");
	}
	
	if (resp[0] != '>') {
	   printf ("dm_down (0) did not receive the proper acknowledgement.\n");
	   return EXIT_FAILURE;
	}
	
	printf ("dm_down successfully shut down the active mirror drivers.\n");
	
	return EXIT_SUCCESS;
}

int dm_clear (int fd)
{
	char cmd[32];
	char resp[32];
	
	strcpy (cmd, "0");
	memset (resp, 0, sizeof (resp));

	if ((send_raw (fd, cmd, resp, sizeof (resp)) != 0)) {
		printf ("dm_down: failed to send command '0'.\n");
	}
	
	if ((strcmp (resp, ">") != 0)) {
		printf ("Warning: dm_down did not receive the proper acknowledgement. Trying again ...\n");
		//printf ("Response is %s\n", resp);
		counter++;
		if (counter > 5) 
		{ 
			printf ("dm_clear: tried to clear driver 5 times without success. Exiting.\n"); 
			return -1; 
		}
		
		dm_clear (fd);
	}
	
	return 0; 
}

int dm_set_bias (driver_t *driver, float bias)
{
	signed short data;
	signed short tmp;
	int i = 0;

	// Convert bias in volts to integer value to send
	// conversion calculated by typing in several different values
	// and assuming a linear relation. MT
	// convert bias in volts to integer value to send
    data = (unsigned short) (bias * (-10.753)) + 884;

	for (i = 0; i < NUM_DRIVERS; i++) 
	{
       driver[i].cbias[0] = 'B';
       tmp =   data >> 8;
       driver[i].cbias[1] = (unsigned char) (data & 0xFF);
       driver[i].cbias[2] = (unsigned char) (tmp & 0xFF);
     }

    for (i = 0; i < NUM_DRIVERS; i++) 
    {
	   if ((send_data_bias(driver[i]) != 0)) 
	   { 
	      printf ("dm_set_bias: failed to set the bias on driver %d.\n", i);
       } else {
          //printf ("dm_set_bias: successfully set the bias on driver %d.\n", i);
       }
     }

     return EXIT_SUCCESS;
}

int dm_mode (driver_t *driver, char* mode)
{
	char cmd[32];
	char resp[32];
	int i;

	if (strcasecmp (mode, "normal") == 0) 
	{
       printf ("Setting mode to normal.\n");
       strcpy (cmd, "MN");
	} else {
		printf ("Setting mode to test.\n");
        strcpy (cmd, "MT");
	}

	// Must bring drivers down to modify the mode //
	if (dm_down (driver[0].fd) == 0) 
	{
       //printf ("dm_down completed successfully.\n");
    } else {
       printf ("dm_down did not complete successfully.\n");
       exit (-1);
    }

	for (i = 0; i < NUM_DRIVERS; i++)
	{
       memset (resp, 0, sizeof (resp));
       if ((send_raw (driver[i].fd, cmd, resp, sizeof (resp)) != 0)) 
       {
          printf ("dm_mode: failed to send the mode command .\n");
       }
       if ((strcmp (resp, ">") != 0)) 
       {
          printf ("dm_mode did not receive the proper acknowledgement.\n");
          return EXIT_FAILURE;
       }
	}
	
	return EXIT_SUCCESS;
}

int dm_status (int fd, int driver_number)
{
	char cmd[4];
	unsigned char resp[1024];
	controller_status cs;
	int i = 0;

	strcpy (cmd, "S");
	memset (resp, 0, sizeof (resp));

	if ((send_raw (fd, cmd, resp, sizeof (resp)) != 0)) {
		printf ("dm_status: failed to send command 'S'.\n");
	}
	
	/**** DEBUG: PRINT OUT HEX DATA ****/
	for (i = 0; i < 17; i++) 
	{ 
	   printf ("%02x ", resp[i]); 
	}
	printf ("\n");
	for (i = 17; i < 298; i++) 
	{ 
	   printf ("%02x ", resp[i]); 
	   if ((i-16) % 28 == 0) { printf ("\n"); }
	}
	printf ("\n");
	
	if (resp[0] != 'S') { 
		printf ("dm_status (S) did not receive the proper acknowledgement.\n");
		return EXIT_FAILURE;
	}

	// We have the status structure in our response string, now we need
	// to format it so we can understand all the bytes and bits 
	if (format_status (&cs, resp) != 0) 
	{
	   printf ("\nERROR: failed to format status message.\n");
	}
	
	// At this point, our cs data structure should now be formatted so
	// we can print out the driver status to screen or file.
	printf ("Status Table for driver %d:\n", driver_number);
	printf ("ready:	%d\n", cs.ready);
	printf ("active: %d\n", cs.active);
	printf ("input bus active: %d\n", cs.ibactive);
	printf ("test mode: %d\n", cs.testmode);
	printf ("mfg mode: %d\n", cs.mfgmode);
	printf ("hard muted: %d\n", cs.hardmuted);
	printf ("bias valid: %d\n", cs.biasvalid);
	printf ("bad board: %d\n", cs.configerror);
	printf ("rail tolerance error: %d\n", cs.powerfail);
	printf ("bias failure: %d\n", cs.biasfail);
	printf ("over temperature: %d\n", cs.overtemp);
	printf ("hardware failure: %d\n", cs.driverfail);
	printf ("fan failure: %d\n", cs.fanfail);
	printf ("near rail: %d\n", cs.nearrail);
	printf ("slew rate failure:	%d\n", cs.slewratefail);
	
	// Loop through the 10 cards and print out the status fields of each card //
	for (i = 0; i < NUM_CARDS; i++) 
	{
		printf ("\nDriver %d, Card %d\n", driver_number, i);
		printf ("D_STAT: %d ", cs.ds[i].stat);
		printf ("ts1: %8.2f |", cs.ds[i].ts1);
		printf ("ts2: %8.2f |", cs.ds[i].ts2);
		printf ("ts3: %8.2f |", cs.ds[i].ts3);
		printf ("ts4: %8.2f |", cs.ds[i].ts4);
		printf ("ts5: %8.2f |", cs.ds[i].ts5);
		printf ("ts6: %8.2f |", cs.ds[i].ts6);
		printf ("ts7: %8.2f |", cs.ds[i].ts7);
		printf ("ts8: %8.2f |", cs.ds[i].ts8);
		printf ("vpp: %8.2f |", cs.ds[i].vpp);
		printf ("vnn: %8.2f |", cs.ds[i].vnn);
		printf ("bias: %8.2f |", cs.ds[i].bias);
		printf ("v25: %8.2f |", cs.ds[i].v25);
		printf ("v33: %8.2f\n", cs.ds[i].v33);
	}

	return 0; 
}

int dm_query (char *qfn, int fd)
{
	int i = 0;
	int j = 0;
	int counter = 0;
	FILE *fp;
	char cmd[4];
	unsigned short temp;
	unsigned char resp[1024];
	voltage_table vt;
	signed short tmp;
	
	strcpy (cmd, "V");
	memset (resp, 0, sizeof (resp));
	if ((send_raw (fd, cmd, resp, sizeof (resp)) != 0)) {
		printf ("issdm_query: failed to send command 'V'.\n");
	}
	
	/**** DEBUG: PRINT OUT HEX DATA ****/
	for (i = 1; i < sizeof (resp); i++) { 
	//	printf ("%02x ", resp[i]); 
		if (((i-1) % 24) == 23) {
	//		printf ("\n");
		}
	}

	/* Populate the Voltage Table Structure with the results from the query */
	vt.cmd = resp[0];
	for (i = 1; i < (NUM_ACTUATORS * 2); i = i + 2) {
	    memcpy (&temp, &resp[i], 2);
	    //printf ("temp = %d  ", temp);
	    //printf ("temp = %d\n", (temp-0x8000));
	    vt.v_table[counter] = counts_to_volts (temp - 0x8000);
	    counter++;
	    temp = 0;
	}
	
	if (qfn != NULL) {
		printf ("Writing to file %s.\n", qfn);
		if ((fp = fopen (qfn, "w+")) == NULL) {
			printf ("issdm_query: unable to open file %s\n", qfn);
		}
		//if ((fwrite (&vt, sizeof(vt), 1, fp)) != 1) {
		//	printf ("dm_query: Error writing to file %s\n", qfn);
		//}
		/* Write ID to the first part of the file */
		if (fprintf(fp, "ID\n\n") < 0) {
			printf ("An error occured while writing the query out to the file %s\n", qfn);
			return -1;
		}
		/* Write actual data */
		for (i = 0; i < NUM_ACTUATORS; i++)
		{
			if (fprintf(fp, "%.4f ", vt.v_table[i]) < 0) {
				printf ("An error occured while writing the query out to the file %s\n", qfn);
				return -1;
			}
			if (((i % 9) == 0) && (i != 0)) {
				if (fprintf(fp, "\n") < 0) {
					printf ("An error occured while writing the query out to the file %s\n", qfn);
					return -1;
				}
			}
			if (((i % 48) == 0) && (i != 0)) {
				if (fprintf(fp, "\n\n") < 0) {
					printf ("An error occured while writing the query out to the file %s\n", qfn);
					return -1;
				}
			}
		}
		/* Write zero's to fill in the rest of the data */
		for (i = 97; i < 480; i++)
		{
			if (fprintf(fp, "0.0 ") < 0) {
				printf ("An error occured while writing the query out to the file %s\n", qfn);
				return -1;
			}
			if ((i % 9) == 0) {
				if (fprintf(fp, "\n") < 0) {
					printf ("An error occured while writing the query out to the file %s\n", qfn);
					return -1;
				}
			}
			if ((i % 48) == 0) {
				if (fprintf(fp, "\n\n") < 0) {
					printf ("An error occured while writing the query out to the file %s\n", qfn);
					return -1;
				}
			}

		}
		fclose (fp);
	} else {
		printf ("\nWriting to standard out.\n");
		printf ("Voltage Table: \n");
		for (i = 0; i < NUM_ACTUATORS; i++) {
			printf ("poke(%d) =  %.4f;\n", i+1, vt.v_table[i]);
		}
	}

	return 0;
}

short volts_to_counts (float volts)
{
    float K = (CMAX - CMIN) / (VMAX - VMIN);
    signed short counts = ((volts - VMIN) * K + CMIN);
    return counts;
}

float counts_to_volts (signed short counts)
{
    float volts = ((float) counts / (CMAX - CMIN)) * (VMAX - VMIN);
	return volts;
}

void print_data (driver_t frame)
{
	int i = 0;
	
	/* print out data */
	printf ("\nData read from file\n--------------\n");
	printf ("id: %X\n", frame.id);
	printf ("data type: %X\n", frame.dt);
	
	for (i = 0; i < sizeof (frame.data); i++) {
		printf ("data[%d]: %X ", i, frame.data[i]);
		if ((i != 0) && ((i % 10) == 0)) printf ("\n");
	}
	printf ("\n");
	
	return;
}

void format_data (driver_t *driver)
{
	int i = 0;
	signed short tmp;
	
	/* clean the text buffer */
	bzero (driver->volts, sizeof (driver->volts));
	
	driver->volts[0] = driver->id;
	driver->volts[1] = driver->dt;
	
	/* i + 2 and i + 3 have to do with the fact that the first two array elements
	 * are taken by the driver id and dt, which are each character elements.
	 */
	for (i = 0; i < FRAME_SIZE; i++)
	{
		tmp = driver->data[i] >> 8;
		driver->volts[(i * 2) + 2] = (unsigned char) (driver->data[i] & 0xFF); 
		driver->volts[(i * 2) + 3] = (unsigned char) (tmp & 0xFF);
	}
	
	return; 
}

void split_data (float dm_data[], driver_t *driver, int driver_num)
{
	int i = 0;
	
	/* All the frames must have ID for the first two characters */
	driver->id = 'I';
	driver->dt = 'D';

	/* clean the text buffer */
	bzero (driver->raw_data, sizeof (driver->raw_data));
	
	/* Put correct data from text into the driver array */
	if (driver_num == 0) {
		for (i = 0; i < ACTUATORS_0; i++) {
			if (D0Map[i] != 0) {
			   driver->raw_data[i] = dm_data[D0Map[i] - 1];
			}
		}
	} else if (driver_num == 1) {
		for (i = 0; i < ACTUATORS_1; i++) {
			if (D1Map[i] != 0) {
			   driver->raw_data[i] = dm_data[D1Map[i] - 1];
			}
		}
	} else if (driver_num == 2)	{
		for (i = 0; i < ACTUATORS_2; i++) {
			if (D2Map[i] != 0) {
			   driver->raw_data[i] = dm_data[D2Map[i] - 1];
			}
		}
	} else if (driver_num == 3)	{
		for (i = 0; i < ACTUATORS_3; i++) {
			if (D3Map[i] != 0) {
			   driver->raw_data[i] = dm_data[D3Map[i] - 1];
			}
		}
	} else if (driver_num == 4)	{
		for (i = 0; i < ACTUATORS_4; i++) {
			if (D4Map[i] != 0) {
			   driver->raw_data[i] = dm_data[D4Map[i] - 1];
			}
		}
	} else if (driver_num == 5)	{
		for (i = 0; i < ACTUATORS_5; i++) {
			if (D5Map[i] != 0) {
			   driver->raw_data[i] = dm_data[D5Map[i] - 1];
			}
		}
	} else if (driver_num == 6)	{
		for (i = 0; i < ACTUATORS_6; i++) {
			if (D6Map[i] != 0) {
			   driver->raw_data[i] = dm_data[D6Map[i] - 1];
			}
		}
	} else {
		for (i = 0; i < ACTUATORS_7; i++) {
			if (D7Map[i] != 0) {
			   driver->raw_data[i] = dm_data[D7Map[i] - 1];
			}
		}
	}
	
	return;
}

/*
 * Status returns 297 bytes (for a 10 card configuration). 
 * Bytes are broken down as follows:
 * Byte 0		= Packet Itentifier
 * Byte (01 & 02)	= Controller Status Word
 * Byte (03 & 04)	= Chassis Status Word
 * Byte (05 & 06)	= Main BIAS Value
 * Byte (07 & 08)	= AUX BIAS Value
 * Byte (09 & 10)	= 24 Volt Rail Monitor
 * Byte (11 & 12)	= Back Plan Temp Sensor
 * Byte (13 & 14)	= Fan Speed
 * Byte (15 & 16)	= Dip Switch Settings
 * Byte (17 - 44)	= Driver 0 Status
 * Byte (45 - 72)	= Driver 1 Status
 * Byte (73 - 100)	= Driver 2 Status
 * Byte (101 - 128)	= Driver 3 Status
 * Byte (129 - 156)	= Driver 4 Status
 * Byte (157 - 184)	= Driver 5 Status
 * Byte (185 - 212)	= Driver 6 Status
 * Byte (213 - 240)	= Driver 7 Status
 * Byte (241 - 268)	= Driver 8 Status
 * Byte (268 - 297)	= Driver 9 Status
 */
int format_status (controller_status *cs, const char* resp)
{
	short temp;
	int i = 0;			/* loop counter */
	int counter = 17;
	
	/* Controller Status */
	cs->ready        = (resp[1] & 0x01);
	cs->active       = (resp[1] & 0x02);
	cs->ibactive     = (resp[1] & 0x04);
	cs->testmode     = (resp[1] & 0x08);
	cs->mfgmode      = (resp[1] & 0x10);
	cs->hardmuted    = (resp[1] & 0x20);
	cs->biasvalid    = (resp[1] & 0x40);
	cs->error        = (resp[1] & 0x80);
	cs->configerror  = (resp[2] & 0x00);
	cs->powerfail    = (resp[2] & 0x02);
	cs->biasfail     = (resp[2] & 0x04);
	cs->overtemp     = (resp[2] & 0x08);
	cs->driverfail   = (resp[2] & 0x10);
	cs->fanfail      = (resp[2] & 0x20);
	cs->nearrail     = (resp[2] & 0x40);
	cs->slewratefail = (resp[2] & 0x80);
	
	/* Chassis Status */
	cs->c_stat.board_10 = resp[3] & 0x40;
	cs->c_stat.board_09 = resp[3] & 0x80;
	cs->c_stat.board_08 = resp[4] & 0x00;
	cs->c_stat.board_07 = resp[4] & 0x02;
	cs->c_stat.board_06 = resp[4] & 0x04;
	cs->c_stat.board_05 = resp[4] & 0x08;
	cs->c_stat.board_04 = resp[4] & 0x10;
	cs->c_stat.board_03 = resp[4] & 0x20;
	cs->c_stat.board_02 = resp[4] & 0x40;
	cs->c_stat.board_01 = resp[4] & 0x80;
	
	/* Main Bias Value */
	memcpy (&temp, &resp[5], 2);
	cs->main_bias_volt = temp;
	temp = 0;

	/* AUX Bias Value */
	memcpy (&temp, &resp[7], 2);
	cs->aux_bias_volt = temp;
	temp = 0;
	
	/* Voltage Rail Monitor */
	memcpy (&temp, &resp[9], 2);
	cs->volt_rail_mon = temp / RAIL_CONV;   
	temp = 0;
	
	/* Back Plan Temperature Sensor */
	memcpy (&temp, &resp[11], 2);
	cs->backplane_temp = temp;
	temp = 0;

	/* Fan Speed Value */
	memcpy (&temp, &resp[13], 2);
	cs->fan_speeds = temp;
	temp = 0;

	/* DIP Switch Values */
	memcpy (&temp, &resp[15], 2);
	cs->dip_switches = temp;
	temp = 0;
	
	for (i = 0; i < NUM_CARDS; i++)
	{
	    // Tmp storage for driver data
		unsigned short tmp = 0;
		
		// Status for driver N 
		memcpy (&tmp, &resp[counter], 2);
		cs->ds[i].stat = tmp;
		counter = counter + 2;
		tmp = 0;							// reset tmp just in case
		
		memcpy (&tmp, &resp[counter], 2);
		cs->ds[i].ts1 = tmp / TS_CONV;
		counter = counter + 2;	
		tmp = 0;
		
		memcpy (&tmp, &resp[counter], 2);
		cs->ds[i].ts2 = tmp / TS_CONV;
		counter = counter + 2;								
		tmp = 0;
		
		memcpy (&tmp, &resp[counter], 2);
		cs->ds[i].ts3 = tmp / TS_CONV;
		counter = counter + 2;								
		tmp = 0;
		
		memcpy (&tmp, &resp[counter], 2);
		cs->ds[i].ts4 = tmp / TS_CONV;
		counter = counter + 2;								
		tmp = 0;
		
		memcpy (&tmp, &resp[counter], 2);
		cs->ds[i].ts5 = tmp / TS_CONV;
		counter = counter + 2;								
		tmp = 0;
		
		memcpy (&tmp, &resp[counter], 2);
		cs->ds[i].ts6 = tmp / TS_CONV;
		counter = counter + 2;								
		tmp = 0;
		
		memcpy (&tmp, &resp[counter], 2);
		cs->ds[i].ts7 = tmp / TS_CONV;
		counter = counter + 2;								
		tmp = 0;
		
		memcpy (&tmp, &resp[counter], 2);
		cs->ds[i].ts8 = tmp / TS_CONV;
		counter = counter + 2;								
		tmp = 0;
		
		memcpy (&tmp, &resp[counter], 2);
		cs->ds[i].vpp = tmp / VPP_CONV;
		counter = counter + 2;								
		tmp = 0;
		
		memcpy (&tmp, &resp[counter], 2);
		cs->ds[i].vnn = (1024 - tmp) / VNN_CONV;
		counter = counter + 2;								
		tmp = 0;
		
		memcpy (&tmp, &resp[counter], 2);
		cs->ds[i].bias = tmp;
		counter = counter + 2;							
		tmp = 0;
		
		memcpy (&tmp, &resp[counter], 2);
		cs->ds[i].v25 = tmp / V25_CONV;
		counter = counter + 2;								
		tmp = 0;
		
		memcpy (&tmp, &resp[counter], 2);
		cs->ds[i].v33 = tmp / V33_CONV;
		counter = counter + 2;
	}

	return EXIT_SUCCESS;
}

int send_data_bias (driver_t driver) {

	struct timeval timeout;
	unsigned char read_buffer[1024];
	unsigned char response[1024];
	fd_set readfs;
	int recv_len;
	int resp_len;
	int status;

	if (driver.cbias == NULL)
    {
    	printf ("Error: send_data_bias: cbias is NULL\n");
        errno = EINVAL;
        return ERROR;
    }

    if (strlen ((char *) driver.cbias) == 0)  
   	{
        printf ("Error: send_data_bias: cbias is empty string\n");
        errno = EINVAL;
        return ERROR;
    }

    memset (driver.resp, 0, sizeof (driver.resp));
    FD_ZERO (&readfs);
    FD_SET (driver.fd, &readfs);

//  printf("send_data_bias: size of comamnd %d\n", sizeof(driver.cbias));
//  printf("send_data_bias data: 0x%x, 0x%x, 0x%x \n", driver.cbias[0],
//  driver.cbias[1], driver.cbias[2]);

	if (write (driver.fd, driver.cbias, (sizeof (driver.cbias))) < 0) 
	{
		printf ("Error: send_data_bias: %s\n", strerror (errno));
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
			printf ("Error: send_data_bias: %s\n", strerror (errno));
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
			printf ("Internal Error: send_data_bias: response buffer too small for data received\n");
			errno = EINVAL;
			return -1;
		}

		/* Read the response */
		if ((len = read (driver.fd, read_buffer, sizeof (response) - recv_len)) < 0) {
			printf ("Error: send_data_bias: %s\n", strerror (errno));
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

//    printf ("Received: [length : %i]\n", recv_len);
    if (driver.resp != NULL)  {
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
