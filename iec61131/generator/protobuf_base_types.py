#!/usr/bin/env python3

"""
Protobuf Base Types for IEC 61131-3
These are general-purpose types that should be included once in the project,
not generated per .proto file.

This module provides individual base type components that can be dynamically
assembled and split according to platform-specific requirements.
"""


class ProtobufBaseTypes:
    """Container for individual protobuf base type definitions"""

    @staticmethod
    def field_descriptor():
        """Field descriptor structure - equivalent to nanoPB pb_field_t"""
        return """(* Field descriptor structure - equivalent to nanoPB pb_field_t *)
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
END_TYPE"""

    @staticmethod
    def message_descriptor():
        """Message descriptor structure - equivalent to nanoPB pb_msgdesc_t"""
        return """(* Message descriptor structure - equivalent to nanoPB pb_msgdesc_t *)
TYPE MESSAGE_DESCRIPTOR :
STRUCT
    field_count : USINT;      (* Number of fields in message *)
    field_info : UDINT;       (* Pointer to field descriptor array *)
    message_size : UINT;      (* Size of message structure *)
    message_name : STRING[50]; (* Message name for debugging *)
END_STRUCT
END_TYPE"""

    @staticmethod
    def pb_stream():
        """Protobuf stream structure for encoding/decoding"""
        return """(* Protobuf stream structure for encoding/decoding *)
TYPE PB_STREAM :
STRUCT
    buffer : UDINT;           (* Pointer to buffer *)
    bytes_written : UINT;     (* Bytes written/read so far *)
    max_size : UINT;          (* Maximum buffer size *)
    error : BOOL;             (* Error flag *)
    error_code : DINT;        (* Detailed error code *)
END_STRUCT
END_TYPE"""

    @staticmethod
    def pb_callback():
        """Protobuf callback function signature"""
        return """(* Protobuf callback function signature *)
TYPE PB_CALLBACK :
STRUCT
    func : UDINT;             (* Pointer to callback function *)
    arg : UDINT;              (* User argument *)
END_STRUCT
END_TYPE"""


class ProtobufBaseConstants:
    """Container for individual protobuf base constant definitions"""

    @staticmethod
    def field_type_constants():
        """Field type constants - equivalent to nanoPB pb_atype_t"""
        return """    (* Field type constants - equivalent to nanoPB pb_atype_t *)
    PB_ATYPE_STATIC : USINT := 0;         (* Static allocation *)
    PB_ATYPE_CALLBACK : USINT := 1;       (* Callback allocation *)"""

    @staticmethod
    def has_type_constants():
        """Has type constants - equivalent to nanoPB pb_htype_t"""
        return """    (* Has type constants - equivalent to nanoPB pb_htype_t *)
    PB_HTYPE_SINGULAR : USINT := 0;       (* Singular field *)
    PB_HTYPE_REPEATED : USINT := 1;       (* Repeated field *)
    PB_HTYPE_ONEOF : USINT := 2;          (* Oneof field *)"""

    @staticmethod
    def length_type_constants():
        """Length type constants - equivalent to nanoPB pb_ltype_t"""
        return """    (* Length type constants - equivalent to nanoPB pb_ltype_t *)
    PB_LTYPE_VARINT : USINT := 1;         (* INT32, BOOL, ENUM *)
    PB_LTYPE_SVARINT : USINT := 2;        (* SINT32, SINT64 *)
    PB_LTYPE_INT64 : USINT := 3;          (* INT64, UINT64 *)
    PB_LTYPE_FIXED32 : USINT := 4;        (* FIXED32, SFIXED32 *)
    PB_LTYPE_FLOAT : USINT := 5;          (* FLOAT *)
    PB_LTYPE_FIXED64 : USINT := 6;        (* FIXED64, SFIXED64, DOUBLE *)
    PB_LTYPE_STRING : USINT := 9;         (* STRING, BYTES *)
    PB_LTYPE_BOOL : USINT := 8;           (* BOOL *)"""

    @staticmethod
    def wire_type_constants():
        """Wire type constants - protobuf wire format"""
        return """    (* Wire type constants - protobuf wire format *)
    PB_WT_VARINT : USINT := 0;            (* Varint *)
    PB_WT_64BIT : USINT := 1;             (* 64-bit *)
    PB_WT_STRING : USINT := 2;            (* Length-delimited *)
    PB_WT_32BIT : USINT := 5;             (* 32-bit *)"""

    @staticmethod
    def error_codes():
        """Error codes"""
        return """    (* Error codes *)
    PB_ERROR_NONE : DINT := 0;
    PB_ERROR_BUFFER_OVERFLOW : DINT := 1;
    PB_ERROR_INVALID_FIELD : DINT := 2;
    PB_ERROR_INVALID_WIRE_TYPE : DINT := 3;
    PB_ERROR_IO_ERROR : DINT := 4;"""

    @staticmethod
    def maximum_sizes():
        """Maximum sizes"""
        return """    (* Maximum sizes *)
    PB_MAX_REQUIRED_FIELDS : USINT := 64;
    PB_MAX_STRING_LENGTH : UINT := 1024;"""


class ProtobufBaseGenerator:
    """Dynamic generator for protobuf base files with platform-aware splitting"""

    def __init__(self, platform_config):
        self.platform_config = platform_config
        self.base_types = ProtobufBaseTypes()
        self.base_constants = ProtobufBaseConstants()

    def generate_header(self, content_type="TYPES"):
        """Generate platform-specific header"""
        platform_name = self.platform_config.platform_name
        return f"""(* ========================================== *)
(* PROTOBUF BASE {content_type} - INCLUDE ONCE *)
(* ========================================== *)
(* Generated for {platform_name} platform *)
(* These are general-purpose {content_type.lower()} for protobuf support *)
(* Do NOT regenerate these for each .proto file *)

"""

    def generate_all_types(self):
        """Generate all base types as single content block"""
        content = self.generate_header("TYPES")
        content += self.base_types.field_descriptor() + "\n\n"
        content += self.base_types.message_descriptor() + "\n\n"
        content += self.base_types.pb_stream() + "\n\n"
        content += self.base_types.pb_callback()
        return content

    def generate_all_constants(self):
        """Generate all base constants as single content block"""
        scope_keyword = self.platform_config.scope_keywords["global_constants"]
        content = self.generate_header("CONSTANTS")
        content += f"{scope_keyword}\n"
        content += self.base_constants.field_type_constants() + "\n\n"
        content += self.base_constants.has_type_constants() + "\n\n"
        content += self.base_constants.length_type_constants() + "\n\n"
        content += self.base_constants.wire_type_constants() + "\n\n"
        content += self.base_constants.error_codes() + "\n\n"
        content += self.base_constants.maximum_sizes() + "\n\n"
        content += "END_VAR"
        return content

    def generate_individual_type(self, type_name):
        """Generate a single base type for single-type-per-file platforms"""
        content = self.generate_header(f"TYPE: {type_name}")

        type_generators = {
            "FIELD_DESCRIPTOR": self.base_types.field_descriptor,
            "MESSAGE_DESCRIPTOR": self.base_types.message_descriptor,
            "PB_STREAM": self.base_types.pb_stream,
            "PB_CALLBACK": self.base_types.pb_callback,
        }

        if type_name in type_generators:
            content += type_generators[type_name]()
        else:
            raise ValueError(f"Unknown base type: {type_name}")

        return content

    def generate_individual_constant_group(self, group_name):
        """Generate a single constant group for single-type-per-file platforms"""
        scope_keyword = self.platform_config.scope_keywords["global_constants"]
        content = self.generate_header(f"CONSTANTS: {group_name}")
        content += f"{scope_keyword}\n"

        constant_generators = {
            "FIELD_TYPES": self.base_constants.field_type_constants,
            "HAS_TYPES": self.base_constants.has_type_constants,
            "LENGTH_TYPES": self.base_constants.length_type_constants,
            "WIRE_TYPES": self.base_constants.wire_type_constants,
            "ERROR_CODES": self.base_constants.error_codes,
            "MAX_SIZES": self.base_constants.maximum_sizes,
        }

        if group_name in constant_generators:
            content += constant_generators[group_name]() + "\n\n"
        else:
            raise ValueError(f"Unknown constant group: {group_name}")

        content += "END_VAR"
        return content

    def get_available_types(self):
        """Get list of available base types for splitting"""
        return ["FIELD_DESCRIPTOR", "MESSAGE_DESCRIPTOR", "PB_STREAM", "PB_CALLBACK"]

    def get_available_constant_groups(self):
        """Get list of available constant groups for splitting"""
        return [
            "FIELD_TYPES",
            "HAS_TYPES",
            "LENGTH_TYPES",
            "WIRE_TYPES",
            "ERROR_CODES",
            "MAX_SIZES",
        ]


# Legacy compatibility functions - these will be deprecated
def generate_protobuf_base_types(platform_config=None):
    """Legacy function - use ProtobufBaseGenerator instead"""
    if platform_config is None:
        # Fallback for platforms without configuration
        return """(* ========================================== *)
(* PROTOBUF BASE TYPES - INCLUDE ONCE *)
(* ========================================== *)
(* These are general-purpose types for protobuf support *)
(* Do NOT regenerate these for each .proto file *)

""" + "\n\n".join(
            [
                ProtobufBaseTypes.field_descriptor(),
                ProtobufBaseTypes.message_descriptor(),
                ProtobufBaseTypes.pb_stream(),
                ProtobufBaseTypes.pb_callback(),
            ]
        )

    generator = ProtobufBaseGenerator(platform_config)
    return generator.generate_all_types()


def generate_protobuf_base_constants(platform_config=None):
    """Legacy function - use ProtobufBaseGenerator instead"""
    if platform_config is None:
        # Fallback for platforms without configuration
        scope_keyword = "VAR_GLOBAL CONSTANT"
        content = """(* ========================================== *)
(* PROTOBUF BASE CONSTANTS - INCLUDE ONCE *)
(* ========================================== *)
(* These are general-purpose constants for protobuf support *)
(* Do NOT regenerate these for each .proto file *)

"""
    else:
        generator = ProtobufBaseGenerator(platform_config)
        return generator.generate_all_constants()

    content += f"{scope_keyword}\n"
    content += (
        "\n\n".join(
            [
                ProtobufBaseConstants.field_type_constants(),
                ProtobufBaseConstants.has_type_constants(),
                ProtobufBaseConstants.length_type_constants(),
                ProtobufBaseConstants.wire_type_constants(),
                ProtobufBaseConstants.error_codes(),
                ProtobufBaseConstants.maximum_sizes(),
            ]
        )
        + "\n\nEND_VAR"
    )
    return content


def generate_protobuf_base_functions(platform_config=None):
    """Generate base protobuf function blocks that are NOT proto-specific"""

    platform_name = (
        platform_config.platform_name if platform_config else "Multi-Platform"
    )

    return f"""(* ========================================== *)
(* PROTOBUF BASE FUNCTIONS - INCLUDE ONCE *)
(* ========================================== *)
(* Generated for {platform_name} platform *)
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
    # Example of new dynamic approach
    print("=== Testing Dynamic Base Type Generation ===\n")

    # Mock platform configs for testing
    class MockBRConfig:
        platform_name = "br"
        file_structure = "multiple_types_per_file"
        scope_keywords = {"global_constants": "VAR_CONSTANT"}

    class MockCodesysConfig:
        platform_name = "codesys"
        file_structure = "single_type_per_file"
        scope_keywords = {"global_constants": "VAR_GLOBAL CONSTANT"}

    # Test B&R (multiple types per file)
    print("B&R Platform (multiple types per file):")
    br_generator = ProtobufBaseGenerator(MockBRConfig())
    print("Types file content:")
    print(br_generator.generate_all_types()[:200] + "...")
    print("\nConstants file content:")
    print(br_generator.generate_all_constants()[:200] + "...")

    # Test Codesys (single type per file)
    print("\n" + "=" * 50)
    print("Codesys Platform (single type per file):")
    codesys_generator = ProtobufBaseGenerator(MockCodesysConfig())
    print("Individual FIELD_DESCRIPTOR type:")
    print(codesys_generator.generate_individual_type("FIELD_DESCRIPTOR")[:200] + "...")
    print("\nIndividual FIELD_TYPES constants:")
    print(
        codesys_generator.generate_individual_constant_group("FIELD_TYPES")[:200]
        + "..."
    )
