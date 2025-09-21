#!/usr/bin/env python3

"""
Protobuf Base Types for IEC 61131-3
These are general-purpose types that should be included once in the project,
not generated per .proto file.
"""


def generate_protobuf_base_types():
    """Generate the base protobuf support types that are NOT proto-specific"""

    return """(* ========================================== *)
(* PROTOBUF BASE TYPES - INCLUDE ONCE *)
(* ========================================== *)
(* These are general-purpose types for protobuf support *)
(* Do NOT regenerate these for each .proto file *)

(* Field descriptor structure - equivalent to nanoPB pb_field_t *)
TYPE FIELD_DESCRIPTOR :
STRUCT
    tag : USINT;              (* Protocol buffer field tag *)
    atype : USINT;            (* Array type: STATIC=0, CALLBACK=1 *)
    htype : USINT;            (* Has type: SINGULAR=0, REPEATED=1 *)
    ltype : USINT;            (* Length type: data type encoding *)
    wireType : USINT;         (* Protobuf wire type *)
    dataSize : UINT;          (* Size of field data in bytes *)
    maxCount : UINT;          (* Maximum array size for repeated fields *)
END_STRUCT
END_TYPE

(* Message descriptor structure - equivalent to nanoPB pb_msgdesc_t *)
TYPE MESSAGE_DESCRIPTOR :
STRUCT
    field_count : USINT;      (* Number of fields in message *)
    field_info : UDINT;       (* Pointer to field descriptor array *)
    message_size : UINT;      (* Size of message structure *)
    message_name : STRING[50]; (* Message name for debugging *)
END_STRUCT
END_TYPE

(* Protobuf stream structure for encoding/decoding *)
TYPE PB_STREAM :
STRUCT
    buffer : UDINT;           (* Pointer to buffer *)
    bytes_written : UINT;     (* Bytes written/read so far *)
    max_size : UINT;          (* Maximum buffer size *)
    error : BOOL;             (* Error flag *)
    error_code : DINT;        (* Detailed error code *)
END_STRUCT
END_TYPE

(* Protobuf callback function signature *)
TYPE PB_CALLBACK :
STRUCT
    func : UDINT;             (* Pointer to callback function *)
    arg : UDINT;              (* User argument *)
END_STRUCT
END_TYPE"""


def generate_protobuf_base_constants():
    """Generate the base protobuf constants that are NOT proto-specific"""

    return """(* ========================================== *)
(* PROTOBUF BASE CONSTANTS - INCLUDE ONCE *)
(* ========================================== *)
(* These are general-purpose constants for protobuf support *)
(* Do NOT regenerate these for each .proto file *)

VAR_GLOBAL CONSTANT
    (* Field type constants - equivalent to nanoPB pb_atype_t *)
    PB_ATYPE_STATIC : USINT := 0;         (* Static allocation *)
    PB_ATYPE_CALLBACK : USINT := 1;       (* Callback allocation *)

    (* Has type constants - equivalent to nanoPB pb_htype_t *)
    PB_HTYPE_SINGULAR : USINT := 0;       (* Singular field *)
    PB_HTYPE_REPEATED : USINT := 1;       (* Repeated field *)
    PB_HTYPE_ONEOF : USINT := 2;          (* Oneof field *)

    (* Length type constants - equivalent to nanoPB pb_ltype_t *)
    PB_LTYPE_VARINT : USINT := 1;         (* INT32, BOOL, ENUM *)
    PB_LTYPE_SVARINT : USINT := 2;        (* SINT32, SINT64 *)
    PB_LTYPE_INT64 : USINT := 3;          (* INT64, UINT64 *)
    PB_LTYPE_FIXED32 : USINT := 4;        (* FIXED32, SFIXED32 *)
    PB_LTYPE_FLOAT : USINT := 5;          (* FLOAT *)
    PB_LTYPE_FIXED64 : USINT := 6;        (* FIXED64, SFIXED64, DOUBLE *)
    PB_LTYPE_STRING : USINT := 9;         (* STRING, BYTES *)
    PB_LTYPE_BOOL : USINT := 8;           (* BOOL *)

    (* Wire type constants - protobuf wire format *)
    PB_WT_VARINT : USINT := 0;            (* Varint *)
    PB_WT_64BIT : USINT := 1;             (* 64-bit *)
    PB_WT_STRING : USINT := 2;            (* Length-delimited *)
    PB_WT_32BIT : USINT := 5;             (* 32-bit *)

    (* Error codes *)
    PB_ERROR_NONE : DINT := 0;
    PB_ERROR_BUFFER_OVERFLOW : DINT := 1;
    PB_ERROR_INVALID_FIELD : DINT := 2;
    PB_ERROR_INVALID_WIRE_TYPE : DINT := 3;
    PB_ERROR_IO_ERROR : DINT := 4;

    (* Maximum sizes *)
    PB_MAX_REQUIRED_FIELDS : USINT := 64;
    PB_MAX_STRING_LENGTH : UINT := 1024;

END_VAR"""


def generate_protobuf_base_functions():
    """Generate base protobuf function blocks that are NOT proto-specific"""

    return """(* ========================================== *)
(* PROTOBUF BASE FUNCTIONS - INCLUDE ONCE *)
(* ========================================== *)
(* These are general-purpose functions for protobuf support *)
(* Do NOT regenerate these for each .proto file *)

(* Initialize a protobuf stream for encoding *)
FUNCTION FB_PB_InitStream : BOOL
VAR_INPUT
    stream : REFERENCE TO PB_STREAM;
    buffer : UDINT;
    max_size : UINT;
END_VAR

stream.buffer := buffer;
stream.bytes_written := 0;
stream.max_size := max_size;
stream.error := FALSE;
stream.error_code := PB_ERROR_NONE;

FB_PB_InitStream := TRUE;

END_FUNCTION

(* Encode a varint value *)
FUNCTION FB_PB_EncodeVarint : BOOL
VAR_INPUT
    stream : REFERENCE TO PB_STREAM;
    value : ULINT;
END_VAR
VAR
    temp_value : ULINT;
    byte_val : USINT;
END_VAR

temp_value := value;

WHILE temp_value > 127 DO
    IF stream.bytes_written >= stream.max_size THEN
        stream.error := TRUE;
        stream.error_code := PB_ERROR_BUFFER_OVERFLOW;
        FB_PB_EncodeVarint := FALSE;
        RETURN;
    END_IF;

    byte_val := TO_USINT(temp_value AND 127) OR 128;
    (* Write byte to buffer - platform specific implementation needed *)
    stream.bytes_written := stream.bytes_written + 1;
    temp_value := temp_value SHR 7;
END_WHILE;

(* Write final byte *)
IF stream.bytes_written >= stream.max_size THEN
    stream.error := TRUE;
    stream.error_code := PB_ERROR_BUFFER_OVERFLOW;
    FB_PB_EncodeVarint := FALSE;
    RETURN;
END_IF;

byte_val := TO_USINT(temp_value);
(* Write byte to buffer - platform specific implementation needed *)
stream.bytes_written := stream.bytes_written + 1;

FB_PB_EncodeVarint := TRUE;

END_FUNCTION

(* Encode a field tag and wire type *)
FUNCTION FB_PB_EncodeTag : BOOL
VAR_INPUT
    stream : REFERENCE TO PB_STREAM;
    tag : USINT;
    wire_type : USINT;
END_VAR
VAR
    tag_value : ULINT;
END_VAR

tag_value := TO_ULINT(tag) SHL 3 OR TO_ULINT(wire_type);
FB_PB_EncodeTag := FB_PB_EncodeVarint(stream, tag_value);

END_FUNCTION"""


if __name__ == "__main__":
    print("Base Types:")
    print(generate_protobuf_base_types())
    print("\nBase Constants:")
    print(generate_protobuf_base_constants())
    print("\nBase Functions:")
    print(generate_protobuf_base_functions())
