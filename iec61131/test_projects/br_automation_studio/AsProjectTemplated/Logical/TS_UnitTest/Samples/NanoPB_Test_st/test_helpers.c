/********************************************************************
 * test_helpers.c
 * Stream initialization and utility functions
 ********************************************************************/

#include <bur/plctypes.h>

#ifdef _DEFAULT_INCLUDES
#include <AsDefault.h>
#endif

#include "pb.h"

/* Helper function to compare floating point values with tolerance */
bool float_equals(float a, float b, float tolerance)
{
	float diff = (a > b) ? (a - b) : (b - a);
	return (diff <= tolerance);
}
