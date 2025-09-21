# B&R Automation Studio Runtime Library

This directory contains the complete nanoPB runtime library for B&R Automation Studio, providing Protocol Buffers encoding and decoding functionality in IEC 61131-3 Structured Text.

## 📦 Library Components

### Core Files
- **`Types.typ`** - Base nanoPB types and message structures
- **`Constants.var`** - Protocol buffer constants and error definitions
- **`IEC.lby`** - B&R library definition file
- **`ProtoSt.fun`** - Function declarations

### Runtime Functions
- **`pb_codec.st`** - Main encode/decode functions
- **`pb_stream.st`** - Stream handling for buffer operations  
- **`pb_varint.st`** - Variable-length integer encoding/decoding
- **`pb_iterator.st`** - Field iteration utilities
- **`pb_fields.st`** - Field processing functions

## 🚀 Usage in B&R Automation Studio

### 1. Import Library
1. Copy all files to your AS project's Logical View
2. Add library reference in your project
3. Include types in your program: `#include "Types.typ"`

### 2. Basic Message Handling
```st
VAR
    sensor_msg : SensorReading_struct;
    buffer : ARRAY[0..255] OF USINT;
    stream : pb_ostream_struct;
END_VAR

// Initialize message
sensor_msg.sensor_id := 1001;
sensor_msg.temperature := 23.5;
sensor_msg.has_alarm_active := TRUE;
sensor_msg.alarm_active := FALSE;

// Create output stream
pb_st_ostream_from_buffer(stream, ADR(buffer), SIZEOF(buffer));

// Encode message
IF pb_st_encode(stream, SensorReading_fields, ADR(sensor_msg)) THEN
    // Success - buffer contains encoded protobuf data
    // stream.bytes_written contains the actual size
END_IF;
```

### 3. Message Structure Generation
Message structures are generated automatically from `.proto` files using the IEC 61131 code generator:

```proto
message SensorReading {
    required int32 sensor_id = 1;
    required float temperature = 2;
    optional bool alarm_active = 3;
}
```

Generates:
```st
TYPE
    SensorReading_struct : STRUCT
        sensor_id : DINT;              // required int32
        temperature : REAL;            // required float  
        has_alarm_active : BOOL;       // optional field flag
        alarm_active : BOOL;           // optional bool
    END_STRUCT;
END_TYPE
```

## 🔧 Technical Details

### Memory Management
- **Static allocation only** - No dynamic memory, suitable for PLC environments
- **Fixed buffer sizes** - All arrays have compile-time known sizes
- **Deterministic execution** - Suitable for real-time control applications

### B&R Specific Adaptations
- Uses B&R memory functions (`brsmemcpy`, `brsmemset`)
- Compatible with B&R data types (`DINT`, `REAL`, `USINT`, etc.)
- Follows B&R coding standards and conventions
- Tested with Automation Studio 4.x

### Wire Format Compatibility
- **100% protobuf compatible** - Can exchange data with any protobuf implementation
- **Little-endian safe** - Handles byte order correctly
- **Cross-platform** - Data encoded on PLC can be decoded by Python, C++, Java, etc.

## 🧪 Testing

Test the library with the sample project in `../../test_projects/br_automation_studio/`:

1. Open the test project in Automation Studio
2. Build and transfer to target (or simulation)
3. Run the test functions to verify encode/decode operations
4. Check results against known good protobuf data

## ⚠️ Limitations

### Current Limitations
- **String fields** - Limited to fixed-length STRING type
- **Repeated fields** - Arrays only, no dynamic lists
- **Nested messages** - Basic support, full nesting in development
- **Extensions** - Not yet supported

### Future Enhancements
- Dynamic string length support
- Advanced repeated field handling
- Complex nested message structures
- Protocol buffer extensions
- Performance optimizations

## 📚 API Reference

### Core Functions

#### `pb_st_encode(stream, fields, src_struct) : BOOL`
Encode a message structure to protobuf format.

#### `pb_st_decode(stream, fields, dest_struct) : BOOL`  
Decode protobuf data into a message structure.

#### `pb_st_ostream_from_buffer(stream, buffer, size) : REFERENCE TO pb_ostream_struct`
Initialize output stream from buffer.

#### `pb_st_istream_from_buffer(stream, buffer, size) : REFERENCE TO pb_istream_struct`
Initialize input stream from buffer.

### Helper Functions

#### `pb_st_encode_varint(stream, value) : BOOL`
Encode variable-length integer.

#### `pb_st_decode_varint(stream, dest) : BOOL`
Decode variable-length integer.

#### `pb_st_encode_string(stream, str) : BOOL`
Encode string field.

#### `pb_st_decode_string(stream, dest, max_size) : BOOL`
Decode string field.

## 🔍 Troubleshooting

### Common Issues

**Error: "Invalid field"**
- Check field descriptor array matches message structure
- Verify field tags and types are correct

**Error: "Buffer overflow"**  
- Increase output buffer size
- Check message size estimation

**Error: "Invalid wire type"**
- Verify protobuf data is not corrupted
- Check endianness of multi-byte values

### Debugging Tips
- Use the error messages in stream.errmsg for diagnosis
- Enable debug logging in test projects
- Compare with known good protobuf implementations

## 📞 Support

For issues specific to the B&R runtime:
1. Check the documentation in `../../docs/`
2. Review test projects for usage examples  
3. Verify B&R Automation Studio compatibility
4. Test with protobuf reference implementations