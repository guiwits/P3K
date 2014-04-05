#include <stdio.h>
#include <stdlib.h>
#include "genIII_masks.h"

int main (int argc, char** argv)
{
	int i = 0;
	int j = 0;
	
	printf ("Mapping for driver 0\n");
	for (i = 0; i < ACTUATORS_0; i++)
	{
		printf ("%d ", D0Map[i]);
	}
	printf ("\n");
	
	printf ("Mapping for driver 1\n");
	for (i = 0; i < ACTUATORS_1; i++)
	{
		printf ("%d ", D1Map[i]);
	}
	printf ("\n");
	
	printf ("Mapping for driver 2\n");
	for (i = 0; i < ACTUATORS_2; i++)
	{
		printf ("%d ", D2Map[i]);
	}
	printf ("\n");
	
	printf ("Mapping for driver 3\n");
	for (i = 0; i < ACTUATORS_3; i++)
	{
		printf ("%d ", D3Map[i]);
	}
	printf ("\n");
	
	printf ("Mapping for driver 4\n");
	for (i = 0; i < ACTUATORS_4; i++)
	{
		printf ("%d ", D4Map[i]);
	}
	printf ("\n");
	
	printf ("Mapping for driver 5\n");
	for (i = 0; i < ACTUATORS_5; i++)
	{
		printf ("%d ", D5Map[i]);
	}
	printf ("\n");
	
    printf ("Mapping for driver 6\n");	
	for (i = 0; i < ACTUATORS_6;i++)
	{
		printf ("%d ", D6Map[i]);
	}
	printf ("\n");
	
	printf ("Mapping for driver 7\n");
	for (i = 0; i < ACTUATORS_7; i++)
	{
		printf ("%d ", D7Map[i]);
	}
	printf ("\n\n");
	
	printf ("Actuator Map\n");
	for (i = 0; i < DMROWS; i++)
	{
		for (j = 0; j < DMCOLS; j++)
		{
			printf ("%d, ", ActuatorMask[i][j]);
		}
		printf ("\n");
	}
	
	return EXIT_SUCCESS;
}
