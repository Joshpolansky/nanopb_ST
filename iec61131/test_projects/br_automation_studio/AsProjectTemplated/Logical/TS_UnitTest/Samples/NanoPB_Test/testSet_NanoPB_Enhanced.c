/* Enhanced nanoPB tests using properly generated structures */
#include <bur/plctypes.h>
#include <AsDefault.h>
#include "UnitTest.h"
#include "test_messages.pb.h"

/* Test variables */
//static USINT test_buffer[1000];
//static pb_ostream_struct output_stream;
//static pb_istream_struct input_stream;

/* Test message instances */
static test_SensorReading sensor_msg;
static test_IntegerTypes int_msg;
static test_SimpleMessage simple_msg;

_SETUP_TEST(void)
{
	/* Clear test buffers and structures */
	memset(&test_buffer, 0, sizeof(test_buffer));
	memset(&sensor_msg, 0, sizeof(sensor_msg));
	memset(&int_msg, 0, sizeof(int_msg));
	memset(&simple_msg, 0, sizeof(simple_msg));
    
	TEST_DONE;
}

_TEARDOWN_TEST(void)
{
	TEST_DONE;
}

/* ===== ENHANCED SENSOR READING TESTS ===== */

_TEST test_nanopb_sensor_reading_encode_decode(void)
{
	test_SensorReading original_msg = test_SensorReading_init_zero;
	test_SensorReading decoded_msg = test_SensorReading_init_zero;
	USINT encoded_buffer[100];
	pb_ostream_struct out_stream;
	pb_istream_struct in_stream;
    
	/* Initialize test message with values */
	original_msg.sensor_id = 12345;
	original_msg.temperature = 23.5f;
	original_msg.has_alarm_active = true;
	original_msg.alarm_active = false;
	original_msg.has_timestamp = true;
	original_msg.timestamp = 1609459200; /* 2021-01-01 00:00:00 UTC */
    
	/* Set up string callback for location (simplified for test) */
	original_msg.location.funcs.encode = NULL; /* We'll skip string encoding for now */
    
	/* Create output stream */
	pb_ostream_from_buffer(encoded_buffer, sizeof(encoded_buffer), &out_stream);
    
	/* Encode message using nanoPB library functions */
	TEST_ASSERT_MESSAGE(pb_encode(&test_SensorReading_msg, &original_msg, &out_stream), 
		"Failed to encode SensorReading with nanoPB");
    
	TEST_ASSERT_MESSAGE(out_stream.bytes_written > 0, "No bytes written during encoding");
	TEST_ASSERT_MESSAGE(out_stream.bytes_written < sizeof(encoded_buffer), "Encoded message too large");
    
	/* Create input stream from encoded data */
	pb_istream_from_buffer(encoded_buffer, out_stream.bytes_written, &in_stream);
    
	/* Initialize decode message */
	memset(&decoded_msg,0,sizeof(decoded_msg));
    
	/* Decode message */
	TEST_ASSERT_MESSAGE(pb_decode(&test_SensorReading_msg, &decoded_msg, &in_stream),
		"Failed to decode SensorReading with nanoPB");
    
	/* Verify decoded data matches original */
	TEST_ASSERT_EQUAL_INT(original_msg.sensor_id, decoded_msg.sensor_id);
	TEST_ASSERT_FLOAT_WITHIN(0.01f, original_msg.temperature, decoded_msg.temperature);
	TEST_ASSERT_EQUAL_INT(original_msg.has_alarm_active, decoded_msg.has_alarm_active);
	TEST_ASSERT_EQUAL_INT(original_msg.alarm_active, decoded_msg.alarm_active);
	TEST_ASSERT_EQUAL_INT(original_msg.has_timestamp, decoded_msg.has_timestamp);
	TEST_ASSERT_EQUAL_INT(original_msg.timestamp, decoded_msg.timestamp);
    
	TEST_INFO("nanoPB SensorReading encode/decode completed successfully");
	TEST_DONE;
}

/* ===== INTEGER TYPES COMPREHENSIVE TEST ===== */

_TEST test_nanopb_integer_types_comprehensive(void)
{
	test_IntegerTypes original_msg = test_IntegerTypes_init_zero;
	test_IntegerTypes decoded_msg;
	USINT encoded_buffer[200];
	pb_ostream_struct out_stream;
	pb_istream_struct in_stream;
    
	/* Initialize with diverse integer values */
	original_msg.int32_field = -2147483648; /* INT32_MIN */
	original_msg.int64_field = -9223372036854775807LL; /* near INT64_MIN */
	original_msg.uint32_field = 4294967295U; /* UINT32_MAX */
	original_msg.uint64_field = 18446744073709551615ULL; /* UINT64_MAX */
	original_msg.sint32_field = -1000000;
	original_msg.sint64_field = 1000000000000LL;
	original_msg.fixed32_field = 0x12345678;
	original_msg.fixed64_field = 0x123456789ABCDEF0ULL;
	original_msg.sfixed32_field = -123456;
	original_msg.sfixed64_field = -123456789012345LL;
    
	/* Encode */
	pb_ostream_from_buffer(encoded_buffer, sizeof(encoded_buffer), &out_stream);
	TEST_ASSERT_MESSAGE(pb_encode(&test_IntegerTypes_msg, &original_msg, &out_stream),
		"Failed to encode IntegerTypes");
    
	/* Decode */
	pb_istream_from_buffer(encoded_buffer, out_stream.bytes_written, &in_stream);
	memset(&decoded_msg,0,sizeof(decoded_msg));
    TEST_ASSERT_MESSAGE(pb_decode(&test_IntegerTypes_msg, &decoded_msg, &in_stream),
                       "Failed to decode IntegerTypes");
    
    /* Verify all integer types */
    TEST_ASSERT_EQUAL_INT(original_msg.int32_field, decoded_msg.int32_field);
    TEST_ASSERT_EQUAL_INT((UDINT)(original_msg.int64_field & 0xFFFFFFFF), (UDINT)(decoded_msg.int64_field & 0xFFFFFFFF));
    TEST_ASSERT_EQUAL_INT(original_msg.uint32_field, decoded_msg.uint32_field);
    TEST_ASSERT_EQUAL_INT((UDINT)(original_msg.uint64_field & 0xFFFFFFFF), (UDINT)(decoded_msg.uint64_field & 0xFFFFFFFF));
    TEST_ASSERT_EQUAL_INT(original_msg.sint32_field, decoded_msg.sint32_field);
    TEST_ASSERT_EQUAL_INT((UDINT)(original_msg.sint64_field & 0xFFFFFFFF), (UDINT)(decoded_msg.sint64_field & 0xFFFFFFFF));
    TEST_ASSERT_EQUAL_INT(original_msg.fixed32_field, decoded_msg.fixed32_field);
    TEST_ASSERT_EQUAL_INT((UDINT)(original_msg.fixed64_field & 0xFFFFFFFF), (UDINT)(decoded_msg.fixed64_field & 0xFFFFFFFF));
    TEST_ASSERT_EQUAL_INT(original_msg.sfixed32_field, decoded_msg.sfixed32_field);
    TEST_ASSERT_EQUAL_INT((UDINT)(original_msg.sfixed64_field & 0xFFFFFFFF), (UDINT)(decoded_msg.sfixed64_field & 0xFFFFFFFF));
    
    TEST_INFO("All integer types encoded/decoded successfully");
TEST_DONE;
}

/* ===== FIELD ITERATION WITH REAL DESCRIPTORS ===== */

_TEST test_nanopb_real_field_iteration(void)
{
	pb_field_iter_struct iter = {0};
	test_SensorReading test_msg = test_SensorReading_init_zero;
	BOOL found_fields[6] = {0}; /* Track fields 1-5 */
	USINT field_count = 0;
    
	/* Initialize field iterator with real nanoPB message descriptor */
	TEST_ASSERT_MESSAGE(pb_field_iter_begin(&test_msg, &iter, &test_SensorReading_msg),
		"Failed to begin field iteration with real descriptors");
    
	/* Iterate through all fields */
	do {
		field_count++;
		TEST_ASSERT_MESSAGE(iter.tag >= 1 && iter.tag <= 5, "Invalid field tag found");
        
		found_fields[iter.tag] = 1; /* Mark field as found */
        
		/* Verify field types match expectations */
		switch(iter.tag) {
			case test_SensorReading_sensor_id_tag: /* 1 - INT32 */
				TEST_ASSERT_EQUAL_INT(PB_LTYPE_VARINT, iter.type & PB_LTYPE_MASK);
				break;
			case test_SensorReading_temperature_tag: /* 2 - FLOAT */
				TEST_ASSERT_EQUAL_INT(PB_LTYPE_FIXED32, iter.type & PB_LTYPE_MASK);
				break;
			case test_SensorReading_alarm_active_tag: /* 3 - BOOL */
				TEST_ASSERT_EQUAL_INT(PB_LTYPE_BOOL, iter.type & PB_LTYPE_MASK);
				break;
			case test_SensorReading_timestamp_tag: /* 4 - INT64 */
				TEST_ASSERT_EQUAL_INT(PB_LTYPE_VARINT, iter.type & PB_LTYPE_MASK);
				break;
			case test_SensorReading_location_tag: /* 5 - STRING */
				TEST_ASSERT_EQUAL_INT(PB_LTYPE_STRING, iter.type & PB_LTYPE_MASK);
				break;
		}
        
	} while(pb_field_iter_next(&iter));
    
	/* Verify all expected fields were found */
	TEST_ASSERT_MESSAGE(found_fields[1], "sensor_id field not found");
	TEST_ASSERT_MESSAGE(found_fields[2], "temperature field not found");
	TEST_ASSERT_MESSAGE(found_fields[3], "alarm_active field not found");
	TEST_ASSERT_MESSAGE(found_fields[4], "timestamp field not found");
	TEST_ASSERT_MESSAGE(found_fields[5], "location field not found");
	TEST_ASSERT_EQUAL_INT(5, field_count);
    
	TEST_INFO("Real nanoPB field iteration completed successfully");
	TEST_DONE;
}

/* ===== COMPATIBILITY TEST ===== */

_TEST test_nanopb_compatibility_check(void)
{
	/* Test that our ST library functions work with real nanoPB structures */
	test_SensorReading msg = test_SensorReading_init_zero;
	pb_ostream_struct out_stream;
	pb_istream_struct in_stream;
	USINT buffer[100];
    
	/* Set some values */
	msg.sensor_id = 42;
	msg.temperature = 25.0f;
    
	/* Test individual encoding functions */
	pb_ostream_from_buffer(buffer, sizeof(buffer), &out_stream);
    
	/* Test varint encoding (sensor_id) */
	TEST_ASSERT_MESSAGE(pb_encode_varint(msg.sensor_id, &out_stream), 
		"ST pb_encode_varint failed with nanoPB data");
    
	/* Test fixed32 encoding (temperature) */
	TEST_ASSERT_MESSAGE(pb_encode_fixed32(*(UDINT*)&msg.temperature, &out_stream),
		"ST pb_encode_fixed32 failed with nanoPB data");
    
	/* Test decoding */
	pb_istream_from_buffer(buffer, out_stream.bytes_written,&in_stream);
    
	UDINT decoded_sensor_id;
	float decoded_temp_bits;
    
	TEST_ASSERT_MESSAGE(pb_decode_varint(&decoded_sensor_id, &in_stream),
		"ST pb_decode_varint failed");
	TEST_ASSERT_MESSAGE(pb_decode_fixed32(&decoded_temp_bits, &in_stream),
		"ST pb_decode_fixed32 failed");
    
	/* Verify decoded values */
	TEST_ASSERT_EQUAL_INT(msg.sensor_id, decoded_sensor_id);
	TEST_ASSERT_FLOAT_WITHIN(0.01f, msg.temperature, decoded_temp_bits);
    
	TEST_INFO("ST library functions compatible with nanoPB structures");
	TEST_DONE;
}


_TEST test_nanopb_generated(void){
	ProtoSystemStatus original_msg = {0};
	ProtoSystemStatus decoded_msg = {0};
	USINT encoded_buffer[100];
	pb_ostream_struct out_stream;
	pb_istream_struct in_stream;
   
	
	/* Populate some test data */
	original_msg.lastReading.has_alarmActive = 1;
	original_msg.lastReading.alarmActive = 1;
       
	/* Create output stream */
	pb_ostream_from_buffer(encoded_buffer, sizeof(encoded_buffer), &out_stream);
    
	/* Encode message using nanoPB library functions */
	TEST_ASSERT_MESSAGE(pb_encode(&SystemStatus_descriptor, &original_msg, &out_stream), "Failed to encode SensorReading with nanoPB");
    
	TEST_ASSERT_MESSAGE(out_stream.bytes_written > 0, "No bytes written during encoding");
	TEST_ASSERT_MESSAGE(out_stream.bytes_written < sizeof(encoded_buffer), "Encoded message too large");
    
	/* Create input stream from encoded data */
	pb_istream_from_buffer(encoded_buffer, out_stream.bytes_written, &in_stream);
    
	/* Initialize decode message */
	memset(&decoded_msg,0,sizeof(decoded_msg));
    
	/* Decode message */
	TEST_ASSERT_MESSAGE(pb_decode(&SystemStatus_descriptor, &decoded_msg, &in_stream),
		"Failed to decode SensorReading with nanoPB");
    
	/* Verify decoded data matches original */
	TEST_ASSERT_EQUAL_INT(original_msg.activeConnections, decoded_msg.activeConnections);
	TEST_ASSERT_FLOAT_WITHIN(0.01f, original_msg.cpuUsage, decoded_msg.cpuUsage);
	TEST_ASSERT_EQUAL_INT(original_msg.has_activeConnections, decoded_msg.has_activeConnections);

	TEST_ASSERT_EQUAL_MEM(&original_msg, &decoded_msg, sizeof(decoded_msg));
	
	
	TEST_INFO("nanoPB SensorReading encode/decode completed successfully");
	TEST_DONE;
}

_TEST test_nanopb_generated_live(void){
	USINT encoded_buffer[100];
	pb_ostream_struct out_stream;
	pb_istream_struct in_stream;
   
	       
	/* Create output stream */
	pb_ostream_from_buffer(encoded_buffer, sizeof(encoded_buffer), &out_stream);
    
	/* Encode message using nanoPB library functions */
	TEST_ASSERT_MESSAGE(pb_encode(&SystemStatus_descriptor, &gSystemStatusIn, &out_stream), "Failed to encode SensorReading with nanoPB");
    
	TEST_ASSERT_MESSAGE(out_stream.bytes_written > 0, "No bytes written during encoding");
	TEST_ASSERT_MESSAGE(out_stream.bytes_written < sizeof(encoded_buffer), "Encoded message too large");
    
	/* Create input stream from encoded data */
	pb_istream_from_buffer(encoded_buffer, out_stream.bytes_written, &in_stream);
    
	/* Initialize decode message */
	memset(&gSystemStatusOut,0,sizeof(gSystemStatusOut));
    
	/* Decode message */
	TEST_ASSERT_MESSAGE(pb_decode(&SystemStatus_descriptor, &gSystemStatusOut, &in_stream),
		"Failed to decode SensorReading with nanoPB");
    
	TEST_ASSERT_EQUAL_MEM(&gSystemStatusIn, &gSystemStatusOut, sizeof(gSystemStatusOut));
	
	
	TEST_INFO("nanoPB SensorReading encode/decode completed successfully");
	TEST_DONE;
}


/*
B+R UnitTest: This is generated code.
Do not edit! Do not move!
Description: UnitTest Testprogramm infrastructure (TestSet).
LastUpdated: 2025-09-22 05:06:55Z
By B+R UnitTest Helper Version: 2.0.0.0
*/
UNITTEST_FIXTURES(fixtures)
{
	new_TestFixture("test_nanopb_sensor_reading_encode_decode", test_nanopb_sensor_reading_encode_decode), 
	new_TestFixture("test_nanopb_integer_types_comprehensive", test_nanopb_integer_types_comprehensive), 
	new_TestFixture("test_nanopb_real_field_iteration", test_nanopb_real_field_iteration), 
	new_TestFixture("test_nanopb_compatibility_check", test_nanopb_compatibility_check), 
	new_TestFixture("test_nanopb_generated", test_nanopb_generated), 
	new_TestFixture("test_nanopb_generated_live", test_nanopb_generated_live), 
};

UNITTEST_CALLER_COMPLETE_EXPLICIT(testSet_NanoPB_Enhanced, "testSet_NanoPB_Enhanced", setupTest, teardownTest, fixtures, 0, 0, 0);

