/* ao.h -- Adaptive Optics Global Declarations */

/* $Id: ao.h,v 1.4 2005/02/25 23:23:55 aocm Exp $ */

/*---------------------------------------------------------------------------*
 |
 | PROJECT:
 |	Palomar Adaptive Optics (PALAO)
 |	Jet Propulsion Laboratory, Pasadena, CA
 |
 | REVISION HISTORY:
 |
 |   Date            By               Description
 |
 | 01-Feb-99     Thang Trinh        Initial Delivery
 |
 | DESCRIPTION:
 |	This header file defines global type definitions and symbolic
 |	constants that are common to all PALAO applications.
 |
 *--------------------------------------------------------------------------*/

#ifndef AO_H
#define AO_H

/* standard definitions */

#ifndef FALSE
#define FALSE	0
#endif

#ifndef TRUE
#define TRUE	1
#endif

#ifndef ERROR
#define ERROR	(-1)
#endif

#ifndef SUCCESS
#define SUCCESS 0
#endif

#ifndef OFF
#define OFF	0
#endif

#ifndef ON
#define ON	1
#endif

#ifndef NULL
#define NULL	0
#endif

#ifndef NULLP
#define NULLP	(char *)0
#endif

#ifndef IN_RANGE
#define IN_RANGE(n,lo,hi) ((lo) <= (n) && (n) <= (hi))
#endif

#ifndef MAX
#define MAX(a,b) ((a) > (b) ? (a) : (b))
#endif

#ifndef MIN
#define MIN(a,b) ((a) < (b) ? (a) : (b))
#endif

#ifndef SWAP
#define SWAP(a,b) ({ long tmp; tmp = (a), (a) = (b), (b) = tmp})
#endif

//extern int sys_nerr;
//extern char *sys_errlist[];

#ifndef SYS_ERRSTR
#define SYS_ERRSTR(_errno) (((unsigned)_errno > sys_nerr) ? \
    "Illegal errno value" : sys_errlist[_errno])
#endif

/* character definitions */

#ifndef EOS
#define EOS '\000'
#endif

#ifndef BELL
#define BELL '\007'
#endif

#ifndef LF
#define LF '\012'
#endif

#ifndef CR
#define CR '\015'
#endif 

/* integer type definitions */

typedef char	i8, I8;			/*  8-bit integer */

typedef short	i16, I16;		/* 16-bit integer */

typedef int	i32, I32;		/* 32-bit integer */

/* bit and boolean type definitions */
 
typedef unsigned char  u8, U8;		/*  8 bits, for bitwise operations */
 
typedef unsigned short u16, U16;	/* 16 bits, for bitwise operations */
 
typedef unsigned int   u32, U32;	/* 32 bits, for bitwise operations */
 
typedef enum {
    false = 0, true = 1
} boolean;

#endif /* #ifndef AO_H */
