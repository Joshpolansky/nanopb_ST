/********************************************************************
* COPYRIGHT -- Bernecker + Rainer
********************************************************************
* Program: NanoPB_Tests
* Author: GitHub Copilot
********************************************************************
* Comprehensive test set for nanoPB Protocol Buffer library
* Tests varint encoding, streams, field iteration, and message encoding
********************************************************************/

#include <bur/plctypes.h>

#ifdef _DEFAULT_INCLUDES
#include <AsDefault.h>
#endif

#include "UnitTest.h"
#include "test_messages.pb.h"  /* Include real nanoPB generated descriptors */

/* Global nanoPB variables (moved from .var file since they use C types) */
static pb_istream_struct input_stream;
static pb_ostream_struct output_stream;
static pb_uint64_struct test_value_uint64;

/* Executed before each test case */
_SETUP_TEST(void)
{
	/* Clear test buffers */
	memset(&test_buffer, 0, sizeof(test_buffer));
//	memset(&test_message, 0, sizeof(test_message));
	memset(&expected_bytes, 0, sizeof(expected_bytes));
	
	/* Reset test variables */
	test_value_uint32 = 0;
	test_value_int32 = 0;
	test_value_uint64.low = 0;
	test_value_uint64.high = 0;
	strcpy(test_string, "");
	expected_length = 0;
	
	TEST_DONE;
}

/* Executed after each test case */
_TEARDOWN_TEST(void)
{
	TEST_DONE;
}

/* ===== VARINT ENCODING TESTS ===== */

_TEST test_varint_encode_small_values(void)
{
	USINT bytes_written;
	
	/* Test encoding of small values (1 byte) */
	pb_st_ostream_from_buffer(&output_stream, test_buffer, sizeof(test_buffer));
	
	/* Encode value 42 - should be single byte 0x2A */
	TEST_ASSERT_MESSAGE(pb_st_encode_varint(&output_stream, 42), "Failed to encode varint 42");
	TEST_ASSERT_EQUAL_INT(1, output_stream.bytes_written);
	TEST_ASSERT_EQUAL_INT(0x2A, test_buffer[0]);
	
	TEST_DONE;
}

_TEST test_varint_encode_large_values(void)
{
	/* Test encoding of larger values (multiple bytes) */
	pb_st_ostream_from_buffer(&output_stream, test_buffer, sizeof(test_buffer));
	
	/* Encode value 300 - should be 0xAC 0x02 */
	TEST_ASSERT_MESSAGE(pb_st_encode_varint(&output_stream, 300), "Failed to encode varint 300");
	TEST_ASSERT_EQUAL_INT(2, output_stream.bytes_written);
	TEST_ASSERT_EQUAL_INT(0xAC, test_buffer[0]);
	TEST_ASSERT_EQUAL_INT(0x02, test_buffer[1]);
	
	TEST_DONE;
}

_TEST test_varint_decode_small_values(void)
{
	UDINT decoded_value;
	
	/* Set up input buffer with encoded value 42 (0x2A) */
	test_buffer[0] = 0x2A;
	pb_st_istream_from_buffer(&input_stream, test_buffer, 1);
	
	/* Decode and verify */
	TEST_ASSERT_MESSAGE(pb_st_decode_varint(&input_stream, &decoded_value), "Failed to decode varint");
	TEST_ASSERT_EQUAL_INT(42, decoded_value);
	TEST_ASSERT_EQUAL_INT(0, input_stream.bytes_left);
	
	TEST_DONE;
}

_TEST test_varint_decode_large_values(void)
{
	UDINT decoded_value;
	
	/* Set up input buffer with encoded value 300 (0xAC 0x02) */
	test_buffer[0] = 0xAC;
	test_buffer[1] = 0x02;
	pb_st_istream_from_buffer(&input_stream, test_buffer, 2);
	
	/* Decode and verify */
	TEST_ASSERT_MESSAGE(pb_st_decode_varint(&input_stream, &decoded_value), "Failed to decode varint");
	TEST_ASSERT_EQUAL_INT(300, decoded_value);
	TEST_ASSERT_EQUAL_INT(0, input_stream.bytes_left);
	
	TEST_DONE;
}

/* ===== ZIGZAG ENCODING TESTS ===== */

_TEST test_zigzag_encode_positive(void)
{
	/* Test ZigZag encoding of positive values */
	pb_st_ostream_from_buffer(&output_stream, test_buffer, sizeof(test_buffer));
	
	/* Encode positive value 42 -> ZigZag = 84 -> varint = 0x54 */
	TEST_ASSERT_MESSAGE(pb_st_encode_svarint(&output_stream, 42), "Failed to encode svarint 42");
	TEST_ASSERT_EQUAL_INT(0x54, test_buffer[0]);
	
	TEST_DONE;
}

_TEST test_zigzag_encode_negative(void)
{
	/* Test ZigZag encoding of negative values */
	pb_st_ostream_from_buffer(&output_stream, test_buffer, sizeof(test_buffer));
	
	/* Encode negative value -42 -> ZigZag = 83 -> varint = 0x53 */
	TEST_ASSERT_MESSAGE(pb_st_encode_svarint(&output_stream, -42), "Failed to encode svarint -42");
	TEST_ASSERT_EQUAL_INT(0x53, test_buffer[0]);
	
	TEST_DONE;
}

_TEST test_zigzag_decode_positive(void)
{
	DINT decoded_value;
	
	/* Set up buffer with ZigZag encoded positive 42 (0x54) */
	test_buffer[0] = 0x54;
	pb_st_istream_from_buffer(&input_stream, test_buffer, 1);
	
	/* Decode and verify */
	TEST_ASSERT_MESSAGE(pb_st_decode_svarint(&input_stream, &decoded_value), "Failed to decode svarint");
	TEST_ASSERT_EQUAL_INT(42, decoded_value);
	
	TEST_DONE;
}

_TEST test_zigzag_decode_negative(void)
{
	DINT decoded_value;
	
	/* Set up buffer with ZigZag encoded negative -42 (0x53) */
	test_buffer[0] = 0x53;
	pb_st_istream_from_buffer(&input_stream, test_buffer, 1);
	
	/* Decode and verify */
	TEST_ASSERT_MESSAGE(pb_st_decode_svarint(&input_stream, &decoded_value), "Failed to decode svarint");
	TEST_ASSERT_EQUAL_INT(-42, decoded_value);
	
	TEST_DONE;
}

/* ===== FIXED32 ENCODING TESTS ===== */

_TEST test_fixed32_encode(void)
{
	/* Test 32-bit fixed encoding (little-endian) */
	pb_st_ostream_from_buffer(&output_stream, test_buffer, sizeof(test_buffer));
	
	/* Encode 0x12345678 -> bytes: 0x78 0x56 0x34 0x12 */
	TEST_ASSERT_MESSAGE(pb_st_encode_fixed32(&output_stream, 0x12345678), "Failed to encode fixed32");
	TEST_ASSERT_EQUAL_INT(4, output_stream.bytes_written);
	TEST_ASSERT_EQUAL_INT(0x78, test_buffer[0]);
	TEST_ASSERT_EQUAL_INT(0x56, test_buffer[1]);
	TEST_ASSERT_EQUAL_INT(0x34, test_buffer[2]);
	TEST_ASSERT_EQUAL_INT(0x12, test_buffer[3]);
	
	TEST_DONE;
}

_TEST test_fixed32_decode(void)
{
	UDINT decoded_value;
	
	/* Set up buffer with little-endian 32-bit value */
	test_buffer[0] = 0x78;
	test_buffer[1] = 0x56;
	test_buffer[2] = 0x34;
	test_buffer[3] = 0x12;
	pb_st_istream_from_buffer(&input_stream, test_buffer, 4);
	
	/* Decode and verify */
	TEST_ASSERT_MESSAGE(pb_st_decode_fixed32(&input_stream, &decoded_value), "Failed to decode fixed32");
	TEST_ASSERT_EQUAL_INT(0x12345678, decoded_value);
	
	TEST_DONE;
}

/* ===== STREAM OPERATION TESTS ===== */

_TEST test_stream_read_write(void)
{
	USINT write_data[] = {0x01, 0x02, 0x03, 0x04};
	USINT read_data[4];
	
	/* Test basic stream write */
	pb_st_ostream_from_buffer(&output_stream, test_buffer, sizeof(test_buffer));
	TEST_ASSERT_MESSAGE(pb_st_write(&output_stream, write_data, 4), "Failed to write to stream");
	TEST_ASSERT_EQUAL_INT(4, output_stream.bytes_written);
	
	/* Verify written data */
	TEST_ASSERT_EQUAL_MEM(write_data, test_buffer, 4);
	
	/* Test basic stream read */
	pb_st_istream_from_buffer(&input_stream, test_buffer, 4);
	TEST_ASSERT_MESSAGE(pb_st_read(&input_stream, read_data, 4), "Failed to read from stream");
	TEST_ASSERT_EQUAL_INT(0, input_stream.bytes_left);
	
	/* Verify read data */
	TEST_ASSERT_EQUAL_MEM(write_data, read_data, 4);
	
	TEST_DONE;
}

_TEST test_stream_buffer_overflow(void)
{
	USINT write_data[10] = {1,2,3,4,5,6,7,8,9,10};
	
	/* Create small output stream */
	pb_st_ostream_from_buffer(&output_stream, test_buffer, 5);
	
	/* Try to write more than buffer can hold */
	TEST_ASSERT_MESSAGE(!pb_st_write(&output_stream, write_data, 10), "Should fail on buffer overflow");
	
	TEST_DONE;
}

_TEST test_stream_underflow(void)
{
	USINT read_data[10];
	
	/* Create input stream with limited data */
	test_buffer[0] = 0x42;
	pb_st_istream_from_buffer(&input_stream, test_buffer, 1);
	
	/* Try to read more than available */
	TEST_ASSERT_MESSAGE(!pb_st_read(&input_stream, read_data, 10), "Should fail on stream underflow");
	
	TEST_DONE;
}

/* ===== STRING SUBSTREAM TESTS ===== */

_TEST test_string_substream(void)
{
	pb_istream_struct substream;
	USINT string_data[] = {0x05, 'H', 'e', 'l', 'l', 'o'}; /* length=5 + "Hello" */
	USINT read_buffer[10];
	
	/* Set up input stream with string data */
	pb_st_istream_from_buffer(&input_stream, string_data, sizeof(string_data));
	
	/* Create substream for string content */
	TEST_ASSERT_MESSAGE(pb_st_make_string_substream(&input_stream, &substream), "Failed to make string substream");
	
	/* Verify substream properties */
	TEST_ASSERT_EQUAL_INT(5, substream.bytes_left); /* String length */
	
	/* Read string content from substream */
	TEST_ASSERT_MESSAGE(pb_st_read(&substream, read_buffer, 5), "Failed to read from substream");
	TEST_ASSERT_EQUAL_MEM("Hello", read_buffer, 5);
	
	/* Close substream */
	TEST_ASSERT_MESSAGE(pb_st_close_string_substream(&input_stream, &substream), "Failed to close substream");
	
	TEST_DONE;
}

/* ===== SENSOR READING MESSAGE TESTS ===== */

_TEST test_sensorreading_encode_decode(void)
{
	test_SensorReading original_message = test_SensorReading_init_zero;
	test_SensorReading decoded_message = test_SensorReading_init_zero;
	pb_ostream_struct out_stream;
	pb_istream_struct in_stream;
	USINT message_buffer[50];
	USINT bytes_written;
	
	/* Create test message using real nanoPB structure */
	original_message.sensor_id = 12345;
	original_message.temperature = 23.5f;
	original_message.has_alarm_active = true;
	original_message.alarm_active = false;
	
	/* Initialize output stream */
	pb_st_ostream_from_buffer(&out_stream, message_buffer, sizeof(message_buffer));
	
	/* Encode message using real nanoPB descriptor and ST library functions */
	TEST_ASSERT_MESSAGE(pb_st_encode(&out_stream, &test_SensorReading_msg, &original_message), 
		"Failed to encode SensorReading message");
	
	bytes_written = out_stream.bytes_written;
	TEST_ASSERT_MESSAGE(bytes_written > 0, "No bytes written during encoding");
	TEST_ASSERT_MESSAGE(bytes_written < sizeof(message_buffer), "Encoded message too large");
	
	/* Initialize input stream with encoded data */
	pb_st_istream_from_buffer(&in_stream, message_buffer, bytes_written);
	
	/* Decode message using real nanoPB descriptor and ST library functions */
	TEST_ASSERT_MESSAGE(pb_st_decode(&in_stream, &test_SensorReading_msg, &decoded_message), 
		"Failed to decode SensorReading message");
	
	/* Verify decoded data matches original */
	TEST_ASSERT_EQUAL_INT(original_message.sensor_id, decoded_message.sensor_id);
	TEST_ASSERT_FLOAT_WITHIN(0.01f, original_message.temperature, decoded_message.temperature);
	TEST_ASSERT_EQUAL_INT(original_message.has_alarm_active, decoded_message.has_alarm_active);
	TEST_ASSERT_EQUAL_INT(original_message.alarm_active, decoded_message.alarm_active);
	
	TEST_INFO("SensorReading encode/decode cycle completed successfully");
	
	TEST_DONE;
}

_TEST test_sensorreading_partial_message(void)
{
	test_SensorReading message = test_SensorReading_init_zero;
	test_SensorReading decoded_message = test_SensorReading_init_zero;
	pb_ostream_struct out_stream;
	pb_istream_struct in_stream;
	USINT message_buffer[50];
	
	/* Create message with only required fields */
	message.sensor_id = 9999;
	message.temperature = -10.5f;
	message.has_alarm_active = false; /* Optional field not set */
	
	/* Encode and decode using real nanoPB descriptor */
	pb_st_ostream_from_buffer(&out_stream, message_buffer, sizeof(message_buffer));
	TEST_ASSERT_MESSAGE(pb_st_encode(&out_stream, &test_SensorReading_msg, &message), 
		"Failed to encode partial message");
	
	pb_st_istream_from_buffer(&in_stream, message_buffer, out_stream.bytes_written);
	TEST_ASSERT_MESSAGE(pb_st_decode(&in_stream, &test_SensorReading_msg, &decoded_message), 
		"Failed to decode partial message");
	
	/* Verify required fields */
	TEST_ASSERT_EQUAL_INT(message.sensor_id, decoded_message.sensor_id);
	TEST_ASSERT_FLOAT_WITHIN(0.01f, message.temperature, decoded_message.temperature);
	
	/* Verify optional field defaults - this is the key test for has flag handling */
	TEST_ASSERT_EQUAL_INT(false, decoded_message.has_alarm_active);
	
	TEST_DONE;
}

_TEST test_sensorreading_field_iteration(void)
{
	pb_field_iter_struct iter = {0};
	test_SensorReading message = test_SensorReading_init_zero; /* Use real nanoPB structure */
	BOOL found_sensor_id = 0, found_temperature = 0, found_alarm = 0;
	
	/* Test field iterator with real nanoPB descriptor */
	TEST_ASSERT_MESSAGE(pb_st_field_iter_begin(&iter, &test_SensorReading_msg, (UDINT*)&message), 
		"Failed to begin field iteration with real descriptor");
	
	/* Iterate through fields */
	do {
		switch(iter.tag) {
			case test_SensorReading_sensor_id_tag: /* tag=1, sensor_id */
				found_sensor_id = 1;
				TEST_ASSERT_EQUAL_INT(PB_LTYPE_VARINT, iter.type & PB_LTYPE_MASK);
				break;
			case test_SensorReading_temperature_tag: /* tag=2, temperature */  
				found_temperature = 1;
				TEST_ASSERT_EQUAL_INT(PB_LTYPE_FIXED32, iter.type & PB_LTYPE_MASK);
				break;
			case test_SensorReading_alarm_active_tag: /* tag=3, alarm_active */
				found_alarm = 1;
				TEST_ASSERT_EQUAL_INT(PB_LTYPE_BOOL, iter.type & PB_LTYPE_MASK);
				/* Verify that pSize points to has flag for optional field */
				TEST_ASSERT_MESSAGE(iter.pSize != 0, "pSize should not be null for optional field");
				break;
		}
	} while(pb_st_field_iter_next(&iter));
	
	/* Verify all expected fields were found */
	TEST_ASSERT_MESSAGE(found_sensor_id, "sensor_id field not found in iteration");
	TEST_ASSERT_MESSAGE(found_temperature, "temperature field not found in iteration");  
	TEST_ASSERT_MESSAGE(found_alarm, "alarm_active field not found in iteration");
	
	TEST_DONE;
}

/* ===== ERROR HANDLING TESTS ===== */

_TEST test_invalid_varint_decode(void)
{
	UDINT decoded_value;
	
	/* Set up buffer with invalid varint (all continuation bits set) */
	memset(test_buffer, 0xFF, 10); /* 10 bytes of 0xFF */
	pb_st_istream_from_buffer(&input_stream, test_buffer, 10);
	
	/* Should fail due to varint overflow */
	TEST_ASSERT_MESSAGE(!pb_st_decode_varint(&input_stream, &decoded_value), "Should fail on invalid varint");
	
	TEST_DONE;
}

_TEST test_stream_error_propagation(void)
{
	/* Test that stream errors are properly propagated */
	pb_st_ostream_from_buffer(&output_stream, test_buffer, 0); /* Zero-size buffer */
	
	/* Any write should fail */
	TEST_ASSERT_MESSAGE(!pb_st_encode_varint(&output_stream, 42), "Should fail on zero-size buffer");
	TEST_ASSERT_MESSAGE(strlen(output_stream.errmsg) > 0, "Error message should be set");
	
	TEST_DONE;
}

/*
B+R UnitTest: This is generated code.
Do not edit! Do not move!
Description: UnitTest Test program infrastructure (TestSet).
*/
UNITTEST_FIXTURES(fixtures)
{
	new_TestFixture("test_varint_encode_small_values", test_varint_encode_small_values),
	new_TestFixture("test_varint_encode_large_values", test_varint_encode_large_values),
	new_TestFixture("test_varint_decode_small_values", test_varint_decode_small_values),
	new_TestFixture("test_varint_decode_large_values", test_varint_decode_large_values),
	new_TestFixture("test_zigzag_encode_positive", test_zigzag_encode_positive),
	new_TestFixture("test_zigzag_encode_negative", test_zigzag_encode_negative),
	new_TestFixture("test_zigzag_decode_positive", test_zigzag_decode_positive),
	new_TestFixture("test_zigzag_decode_negative", test_zigzag_decode_negative),
	new_TestFixture("test_fixed32_encode", test_fixed32_encode),
	new_TestFixture("test_fixed32_decode", test_fixed32_decode),
	new_TestFixture("test_stream_read_write", test_stream_read_write),
	new_TestFixture("test_stream_buffer_overflow", test_stream_buffer_overflow),
	new_TestFixture("test_stream_underflow", test_stream_underflow),
	new_TestFixture("test_string_substream", test_string_substream),
	new_TestFixture("test_sensorreading_encode_decode", test_sensorreading_encode_decode),
	new_TestFixture("test_sensorreading_partial_message", test_sensorreading_partial_message),
	new_TestFixture("test_sensorreading_field_iteration", test_sensorreading_field_iteration),
	new_TestFixture("test_invalid_varint_decode", test_invalid_varint_decode),
	new_TestFixture("test_stream_error_propagation", test_stream_error_propagation),
};

UNITTEST_CALLER_COMPLETE_EXPLICIT(testSet_NanoPB, "nanoPB Protocol Buffer Tests", setupTest, teardownTest, fixtures, 0, 0, 0);