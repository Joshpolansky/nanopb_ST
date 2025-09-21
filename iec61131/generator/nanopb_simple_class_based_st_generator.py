#!/usr/bin/env python3

"""
nanoPB Simple Class-Based ST Generator - IEC 61131-3 Structured Text code generator
Uses nanoPB's ProtoFile/Message/Field classes with composition rather than inheritance
"""

import sys
import os
import subprocess
import tempfile
from pathlib import Path

# Add the parent generator directory to Python path for nanopb imports
current_dir = os.path.dirname(os.path.abspath(__file__))
generator_dir = os.path.join(current_dir, "..", "..", "generator")
sys.path.insert(0, os.path.abspath(generator_dir))

try:
    from nanopb_generator import ProtoFile, Field, Message, descriptor
    import google.protobuf.descriptor_pb2 as descriptor_pb2

    # Import the field descriptor for type constants
    FieldD = descriptor.FieldDescriptorProto
    
    # Import nanopb_pb2 for proper options
    try:
        import nanopb_pb2
    except ImportError:
        # Try to import from proto directory if available
        sys.path.insert(0, os.path.join(os.path.abspath(generator_dir), 'proto'))
        import nanopb_pb2
        
except ImportError as e:
    print(f"Error importing nanopb_generator: {e}", file=sys.stderr)
    print("Make sure you're running from the correct directory", file=sys.stderr)
    sys.exit(1)


class STFieldWrapper:
    """Wrapper for nanoPB Field providing ST-specific methods"""
    
    # ST type mapping from nanoPB pbtype (string values)
    ST_TYPE_MAP = {
        "BOOL": "BOOL",
        "DOUBLE": "LREAL",
        "FLOAT": "REAL",
        "INT32": "DINT",
        "INT64": "LINT",
        "UINT32": "UDINT",
        "UINT64": "ULINT",
        "SINT32": "DINT",
        "SINT64": "LINT",
        "FIXED32": "UDINT",
        "FIXED64": "ULINT",
        "SFIXED32": "DINT",
        "SFIXED64": "LINT",
        "STRING": "STRING",
        "BYTES": "ARRAY OF USINT",
        "ENUM": "DINT",
        "MESSAGE": "DINT",  # Placeholder for nested messages
    }
    
    def __init__(self, nanopb_field):
        """Initialize with existing nanoPB Field object"""
        self.field = nanopb_field
    
    @property 
    def st_type(self):
        """Get ST type using nanoPB's sophisticated type analysis"""
        base_type = self.ST_TYPE_MAP.get(self.field.pbtype, "DINT")
        
        # Handle string/bytes sizing using nanoPB's max_size
        if self.field.pbtype == "STRING":
            max_size = getattr(self.field, 'max_size', None)
            if max_size and max_size > 0:
                return f"STRING[{max_size-1}]"  # -1 for null terminator
            return "STRING[255]"  # Default
            
        elif self.field.pbtype == "BYTES":
            max_size = getattr(self.field, 'max_size', None)
            if max_size and max_size > 0:
                return f"ARRAY[0..{max_size-1}] OF USINT"
            return "ARRAY[0..255] OF USINT"  # Default
            
        return base_type
    
    @property
    def st_name(self):
        """Convert field name to ST camelCase convention"""
        components = self.field.name.split("_")
        return components[0] + "".join(word.capitalize() for word in components[1:])
    
    def is_plc_compatible(self):
        """Check if field uses PLC-compatible allocation (not CALLBACK)"""
        # Use nanoPB's allocation analysis
        if hasattr(self.field, 'allocation'):
            return str(self.field.allocation) != 'PB_ATYPE_CALLBACK'
        
        # For repeated fields without fixed size, nanoPB uses callbacks
        if self.field.rules == "REPEATED":
            max_count = getattr(self.field, 'max_count', None)
            return max_count and max_count > 0
            
        # String/bytes without fixed size use callbacks
        if self.field.pbtype in ["STRING", "BYTES"]:
            max_size = getattr(self.field, 'max_size', None)
            return max_size and max_size > 0
            
        return True
    
    def has_presence_field(self):
        """Check if this optional field needs a 'has_' presence indicator"""
        # Use the field's descriptor directly (field.desc is the FieldDescriptorProto)
        if hasattr(self.field, 'desc') and hasattr(self.field.desc, 'proto3_optional') and self.field.desc.proto3_optional:
            return True
        return self.field.rules == "OPTIONAL" and self.field.pbtype != "MESSAGE"
    
    def st_field_declarations(self):
        """Generate ST field declaration(s) - may return multiple lines for repeated fields"""
        declarations = []
        
        if not self.is_plc_compatible():
            declarations.append(f"    (* {self.st_name} : SKIPPED - nanoPB CALLBACK field not supported in PLC *)")
            return declarations
        
        # Add has field for optional fields
        if self.has_presence_field():
            declarations.append(f"    has_{self.st_name} : BOOL;  (* nanoPB optional field presence indicator *)")
        
        # Handle repeated fields with nanoPB's max_count
        if self.field.rules == "REPEATED":
            max_count = getattr(self.field, 'max_count', None)
            if max_count is None or max_count <= 0:
                max_count = 10  # Default fallback
            declarations.append(f"    {self.st_name} : ARRAY[0..{max_count-1}] OF {self.st_type};")
            declarations.append(f"    {self.st_name}_count : UINT;  (* Number of valid elements *)")
        else:
            # Single field
            declarations.append(f"    {self.st_name} : {self.st_type};")
            
        return declarations
    
    def st_field_descriptor(self, is_last=False):
        """Generate field descriptor entry using nanoPB's metadata"""
        if not self.is_plc_compatible():
            return []  # Skip CALLBACK fields
        
        # Use nanoPB's sophisticated type analysis
        tag = self.field.tag
        
        # Allocation type from nanoPB (PLC-compatible fields are STATIC)
        atype = 0  # PB_ATYPE_STATIC
        
        # Header type from nanoPB rules
        htype_map = {
            "SINGULAR": 0,  # PB_HTYPE_SINGULAR
            "REPEATED": 1,  # PB_HTYPE_REPEATED  
            "OPTIONAL": 0,  # PB_HTYPE_SINGULAR
        }
        htype = htype_map.get(self.field.rules, 0)
        
        # Low-level type from nanoPB pbtype (string values)
        ltype_map = {
            "BOOL": 8,      # PB_LTYPE_BOOL
            "INT32": 1,     # PB_LTYPE_VARINT
            "INT64": 1,     # PB_LTYPE_VARINT
            "UINT32": 1,    # PB_LTYPE_VARINT
            "UINT64": 1,    # PB_LTYPE_VARINT
            "SINT32": 2,    # PB_LTYPE_SVARINT
            "SINT64": 2,    # PB_LTYPE_SVARINT
            "FIXED32": 4,   # PB_LTYPE_FIXED32
            "FIXED64": 6,   # PB_LTYPE_FIXED64
            "SFIXED32": 4,  # PB_LTYPE_FIXED32
            "SFIXED64": 6,  # PB_LTYPE_FIXED64
            "FLOAT": 5,     # PB_LTYPE_FIXED32
            "DOUBLE": 6,    # PB_LTYPE_FIXED64
            "STRING": 9,    # PB_LTYPE_STRING
            "BYTES": 9,     # PB_LTYPE_STRING
            "ENUM": 1,      # PB_LTYPE_VARINT
            "MESSAGE": 10,  # PB_LTYPE_SUBMSG
        }
        ltype = ltype_map.get(self.field.pbtype, 1)
        
        # Wire type from nanoPB (simplified)
        wire_type = 0  # Most fields use VARINT wire type
        
        # Data size from nanoPB analysis
        data_size = 4  # Default size for most types
        if hasattr(self.field, 'data_item_size') and self.field.data_item_size:
            data_size = self.field.data_item_size
        elif hasattr(self.field, 'data_size'):
            try:
                data_size = self.field.data_size()
            except:
                data_size = 4
        
        # Max count from nanoPB  
        max_count = getattr(self.field, 'max_count', None)
        if self.field.rules == "REPEATED":
            if max_count is None or max_count <= 0:
                max_count = 10  # Use our default for repeated fields
        else:
            max_count = 1  # Singular fields always have count 1
            
        comma = "," if not is_last else ""
        
        lines = []
        lines.append(f"        (* {self.field.name}: {self.st_type} {self.field.rules} *)")
        lines.append(f"        (tag := {tag}, atype := {atype}, htype := {htype}, "
                    f"ltype := {ltype}, wireType := {wire_type}, dataSize := {data_size}, maxCount := {max_count}){comma}")
        
        return lines


class STMessageWrapper:
    """Wrapper for nanoPB Message providing ST-specific methods"""
    
    def __init__(self, nanopb_message):
        """Initialize with existing nanoPB Message object"""
        self.message = nanopb_message
        self.st_fields = [STFieldWrapper(field) for field in nanopb_message.fields]
    
    @property
    def st_struct_name(self):
        """Generate ST struct name"""
        msg_name = str(self.message.name)
        return f"Proto{msg_name}"
    
    def st_struct_declaration(self):
        """Generate ST struct definition using nanoPB field analysis"""
        lines = []
        msg_name = str(self.message.name)
        lines.append(f"(* Message: {msg_name} *)")
        lines.append(f"TYPE {self.st_struct_name} :")
        lines.append("STRUCT")
        
        for field in self.st_fields:
            field_lines = field.st_field_declarations()
            lines.extend(field_lines)
        
        lines.append("END_STRUCT")
        lines.append("END_TYPE")
        lines.append("")
        
        return "\n".join(lines)
    
    def st_field_descriptors(self):
        """Generate field descriptor array using nanoPB metadata"""
        # Only include PLC-compatible fields
        compatible_fields = [f for f in self.st_fields if f.is_plc_compatible()]
        
        if not compatible_fields:
            msg_name = str(self.message.name)
            return [f"    (* {msg_name}: No STATIC fields - all CALLBACK (skipped for PLC) *)"]
        
        lines = []
        msg_name = str(self.message.name)
        lines.append(f"    (* {msg_name} enhanced field descriptors from nanoPB *)")
        lines.append(f"    {msg_name}_nanopb_fields : ARRAY[0..{len(compatible_fields)-1}] OF FIELD_DESCRIPTOR := [")
        
        for i, field in enumerate(compatible_fields):
            is_last = (i == len(compatible_fields) - 1)
            field_lines = field.st_field_descriptor(is_last)
            lines.extend(field_lines)
        
        lines.append("    ];")
        return lines
    
    def st_message_descriptor(self):
        """Generate message descriptor structure (for runtime initialization)"""
        compatible_fields = [f for f in self.st_fields if f.is_plc_compatible()]
        field_count = len(compatible_fields)
        msg_name = str(self.message.name)
        
        lines = []
        lines.append(f"    (* Message descriptor for {msg_name} - initialized at runtime *)")
        lines.append(f"    {msg_name}_descriptor : MESSAGE_DESCRIPTOR;")
        return lines


class STProtoFileWrapper:
    """Wrapper for nanoPB ProtoFile providing ST-specific methods"""
    
    def __init__(self, nanopb_proto_file):
        """Initialize with existing nanoPB ProtoFile object"""
        self.proto_file = nanopb_proto_file
        self.st_messages = [STMessageWrapper(msg) for msg in nanopb_proto_file.messages]
    
    def _get_st_ltype(self, field):
        """Get the ST ltype value for a field"""
        ltype_map = {
            "BOOL": 8,      # PB_LTYPE_BOOL
            "INT32": 1,     # PB_LTYPE_VARINT
            "INT64": 1,     # PB_LTYPE_VARINT
            "UINT32": 1,    # PB_LTYPE_VARINT
            "UINT64": 1,    # PB_LTYPE_VARINT
            "SINT32": 2,    # PB_LTYPE_SVARINT
            "SINT64": 2,    # PB_LTYPE_SVARINT
            "FIXED32": 4,   # PB_LTYPE_FIXED32
            "FIXED64": 6,   # PB_LTYPE_FIXED64
            "SFIXED32": 4,  # PB_LTYPE_FIXED32
            "SFIXED64": 6,  # PB_LTYPE_FIXED64
            "FLOAT": 5,     # PB_LTYPE_FIXED32
            "DOUBLE": 6,    # PB_LTYPE_FIXED64
            "STRING": 9,    # PB_LTYPE_STRING
            "BYTES": 9,     # PB_LTYPE_STRING
            "ENUM": 1,      # PB_LTYPE_VARINT
            "MESSAGE": 10,  # PB_LTYPE_SUBMSG
        }
        return ltype_map.get(field.pbtype, 1)
    
    def _get_st_type(self, pbtype):
        """Get the ST type for a protobuf type"""
        ST_TYPE_MAP = {
            "BOOL": "BOOL",
            "INT32": "DINT", 
            "INT64": "LINT",
            "UINT32": "UDINT",
            "UINT64": "ULINT",
            "SINT32": "DINT",
            "SINT64": "LINT", 
            "FIXED32": "UDINT",
            "FIXED64": "ULINT",
            "SFIXED32": "DINT",
            "SFIXED64": "LINT",
            "FLOAT": "REAL",
            "DOUBLE": "LREAL",
            "STRING": "STRING",
            "BYTES": "ARRAY OF BYTE",
            "ENUM": "DINT",
            "MESSAGE": "STRUCT",
        }
        return ST_TYPE_MAP.get(pbtype, "DINT")
    
    def generate_st_types(self):
        """Generate .typ file content using nanoPB analysis"""
        lines = []
        lines.append(f"(* Generated ST Types from {self.proto_file.fdesc.name} *)")
        lines.append("(* Generated by nanoPB Simple Class-Based ST Generator *)")
        lines.append("(* Uses nanoPB ProtoFile/Message/Field analysis via composition *)")
        lines.append("(* Include protobuf_base.typ for base protobuf types *)")
        lines.append("")
        
        for msg in self.st_messages:
            lines.append(msg.st_struct_declaration())
        
        return "\n".join(lines)
    
    def generate_st_constants(self):
        """Generate .var file content using nanoPB analysis"""
        lines = []
        lines.append(f"(* Generated ST Constants from {self.proto_file.fdesc.name} *)")
        lines.append("(* Generated by nanoPB Simple Class-Based ST Generator *)")
        lines.append("(* Uses nanoPB field analysis for accurate descriptors *)")
        lines.append("(* Include protobuf_base.var for base protobuf constants *)")
        lines.append("")
        lines.append("VAR_GLOBAL CONSTANT")
        
        # Message IDs
        lines.append("")
        lines.append("    (* Message Type IDs *)")
        for i, msg in enumerate(self.st_messages, 1):
            msg_name = str(msg.message.name)
            lines.append(f"    {msg_name.upper()}_MSG_ID : DINT := {i};")
        
        # Add field tags for PLC-compatible fields only
        for msg in self.st_messages:
            compatible_fields = [f for f in msg.st_fields if f.is_plc_compatible()]
            if compatible_fields:
                lines.append("")
                msg_name = str(msg.message.name)
                lines.append(f"    (* {msg_name} field tags - STATIC fields only *)")
                for field in compatible_fields:
                    field_const = f"{msg_name.upper()}_{field.field.name.upper()}_TAG"
                    lines.append(f"    {field_const} : DINT := {field.field.tag};")
        
        # Add global constant instances for offset calculations
        lines.append("")
        lines.append("    (* ========================================== *)")
        lines.append("    (* MESSAGE INSTANCES - For offset calculations *)")
        lines.append("    (* ========================================== *)")
        lines.append("    (* Constant instances used by InitializeProtobufDescriptors *)")
        
        for msg in self.st_messages:
            compatible_fields = [f for f in msg.st_fields if f.is_plc_compatible()]
            if compatible_fields:
                msg_name = str(msg.message.name)
                lines.append("")
                lines.append(f"    (* Constant instance for {msg_name} field offset calculations *)")
                lines.append(f"    {msg_name.upper()}_INSTANCE : {msg.st_struct_name};")
        
        # Enhanced field descriptor arrays using nanoPB metadata
        lines.append("")
        lines.append("    (* ========================================== *)")
        lines.append("    (* ENHANCED FIELD DESCRIPTOR ARRAYS *)")
        lines.append("    (* ========================================== *)")
        lines.append("    (* Generated using nanoPB class-based analysis *)")
        
        for msg in self.st_messages:
            lines.append("")
            descriptor_lines = msg.st_field_descriptors()
            lines.extend(descriptor_lines)
        
        lines.append("")
        lines.append("END_VAR")
        
        # Add non-constant global variables (message descriptors)
        lines.append("")
        lines.append("VAR_GLOBAL")
        lines.append("    (* ========================================== *)")
        lines.append("    (* MESSAGE DESCRIPTORS - Runtime Initialized *)")
        lines.append("    (* ========================================== *)")
        lines.append("    (* Call InitializeProtobufDescriptors() to populate these *)")
        
        for msg in self.st_messages:
            compatible_fields = [f for f in msg.st_fields if f.is_plc_compatible()]
            if compatible_fields:
                lines.append("")
                message_descriptor_lines = msg.st_message_descriptor()
                lines.extend(message_descriptor_lines)
        
        lines.append("")
        lines.append("END_VAR")
        lines.append("")
        
        return "\n".join(lines)
    
    def generate_st_initialization_program(self):
        """Generate ST program for message descriptor initialization"""
        lines = []
        lines.append("(* Protobuf Message Descriptor Initialization Program *)")
        lines.append("(* Run this once during system startup to initialize field descriptors *)")
        lines.append("PROGRAM InitializeProtobufDescriptors")
        lines.append("VAR")
        lines.append("    initialized : BOOL := FALSE;")
        lines.append("END_VAR")
        lines.append("")
        
        lines.append("IF NOT initialized THEN")
        lines.append("")
        
        # Initialize field descriptors with proper addressing - use arrays from .var file
        lines.append("    (* Initialize field descriptors with runtime addressing *)")
        for message in self.proto_file.messages:
            msg_name = str(message.name)
            lines.append(f"    (* Initialize {msg_name} field descriptors *)")
            
            for i, field in enumerate(message.fields):
                field_array = f"{msg_name}_nanopb_fields"
                
                lines.append(f"    (* Field[{i}]: {msg_name}.{str(field.name)} *)")
                lines.append(f"    {field_array}[{i}].data_offset := ADR({msg_name.upper()}_INSTANCE.{str(field.name)}) - ADR({msg_name.upper()}_INSTANCE);")
                lines.append(f"    {field_array}[{i}].size_offset := 0; (* Static size *)")
                lines.append("")
        
        lines.append("    initialized := TRUE;")
        lines.append("END_IF;")
        lines.append("")
        lines.append("END_PROGRAM")
        lines.append("")
        
        return "\n".join(lines)


def generate_st_from_proto_simple_class_based(proto_file_path, output_dir=None):
    """Main function using nanoPB simple class-based approach"""
    
    if output_dir is None:
        output_dir = os.path.dirname(proto_file_path)
    
    base_name = Path(proto_file_path).stem
    
    try:
        # Use protoc to generate FileDescriptor
        with tempfile.NamedTemporaryFile(suffix='.pb', delete=False) as tmp_file:
            tmp_file_path = tmp_file.name
        
        try:
            # Get protoc path
            protoc_path = os.path.join(current_dir, "..", "..", "generator", "protoc.bat")
            if not os.path.exists(protoc_path):
                protoc_path = os.path.join(current_dir, "..", "..", "generator", "protoc")
            if not os.path.exists(protoc_path):
                protoc_path = "protoc"  # System protoc
            
            # Generate descriptor set
            proto_dir = os.path.dirname(os.path.abspath(proto_file_path))
            proto_abs_path = os.path.abspath(proto_file_path)
            
            cmd = [
                protoc_path,
                f'--descriptor_set_out={tmp_file_path}',
                '--include_imports',
                f'--proto_path={proto_dir}',
                proto_abs_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"protoc failed: {result.stderr}")
            
            # Parse FileDescriptorSet
            with open(tmp_file_path, 'rb') as f:
                fds_data = f.read()
            
            file_descriptor_set = descriptor_pb2.FileDescriptorSet()
            file_descriptor_set.ParseFromString(fds_data)
            
            # Find target file descriptor
            target_fdesc = None
            for fdesc in file_descriptor_set.file:
                if os.path.basename(fdesc.name) == os.path.basename(proto_file_path):
                    target_fdesc = fdesc
                    break
            
            if target_fdesc is None:
                raise RuntimeError("Could not find proto file in descriptor set")
            
            # Create nanoPB ProtoFile using proper options
            print("🔧 Creating nanoPB ProtoFile...")
            options = nanopb_pb2.NanoPBOptions()
            nanopb_proto_file = ProtoFile(target_fdesc, options)
            
            print(f"✅ Successfully parsed {len(nanopb_proto_file.messages)} messages using nanoPB")
            
            # Wrap with ST functionality
            print("🎨 Wrapping with ST functionality...")
            st_proto_file = STProtoFileWrapper(nanopb_proto_file)
            
            # Generate base types if needed
            try:
                from protobuf_base_types import (
                    generate_protobuf_base_types,
                    generate_protobuf_base_constants,
                )
                
                base_typ_file = os.path.join(output_dir, "protobuf_base.typ")
                base_var_file = os.path.join(output_dir, "protobuf_base.var")
                
                if not os.path.exists(base_typ_file):
                    with open(base_typ_file, "w") as f:
                        f.write(generate_protobuf_base_types())
                    print("✅ Generated base types: protobuf_base.typ")
                    
                if not os.path.exists(base_var_file):
                    with open(base_var_file, "w") as f:
                        f.write(generate_protobuf_base_constants())
                    print("✅ Generated base constants: protobuf_base.var")
            except ImportError:
                print("⚠️  Base types module not found - continuing without base files")
            
            # Generate ST files using nanoPB class-based approach
            print("🎨 Generating ST files using nanoPB classes via composition...")
            typ_content = st_proto_file.generate_st_types()
            var_content = st_proto_file.generate_st_constants()
            prg_content = st_proto_file.generate_st_initialization_program()
            
            # Write output files
            os.makedirs(output_dir, exist_ok=True)
            
            # .typ file
            typ_file = os.path.join(output_dir, f"{base_name}.typ")
            with open(typ_file, "w") as f:
                f.write(typ_content)
            
            # .var file
            var_file = os.path.join(output_dir, f"{base_name}.var")
            with open(var_file, "w") as f:
                f.write(var_content)
            
            # .prg file (program implementation)
            prg_file = os.path.join(output_dir, f"{base_name}_init.prg")
            with open(prg_file, "w") as f:
                f.write(prg_content)
            
            print("🎉 Generated ST files using nanoPB simple class-based approach:")
            print(f"  ✅ {typ_file}")
            print(f"  ✅ {var_file}")
            print(f"  ✅ {prg_file} (initialization program)")
            
            return True
            
        finally:
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python nanopb_simple_class_based_st_generator.py <proto_file> [output_dir]")
        sys.exit(1)
        
    proto_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    if generate_st_from_proto_simple_class_based(proto_file, output_dir):
        print("\n✨ nanoPB Simple Class-Based ST generation completed successfully!")
    else:
        print("\n💥 nanoPB Simple Class-Based ST generation failed!")
        sys.exit(1)