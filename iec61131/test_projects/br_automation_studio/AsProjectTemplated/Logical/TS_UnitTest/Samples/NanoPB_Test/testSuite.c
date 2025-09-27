/********************************************************************
 * COPYRIGHT -- Bernecker + Rainer
 ********************************************************************
 * Program: NanoPB_Tests
 * Author: GitHub Copilot
 ********************************************************************
 * Test suite registration and control for nanoPB library
 ********************************************************************/

#include <bur/plctypes.h>

#ifdef _DEFAULT_INCLUDES
#include <AsDefault.h>
#endif

#include "UnitTest.h"

void _INIT initTestSuite(void)
{
	utInit(&Testsuite);
}

void _CYCLIC cyclicWithTest(void)
{
	/* Run test suite cyclically */
	utCyclic(&Testsuite);
}

void _EXIT exitTestSuite(void)
{
	utExit(&Testsuite);
}