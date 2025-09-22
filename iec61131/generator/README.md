# IEC 61131-3 Code Generators

This directory contains the code generators for converting Protocol Buffer (`.proto`) files into IEC 61131-3 Structured Text code for different automation platforms.

## 🏗️ Architecture

The generator system consists of two main components:

### 1. Message Code Generator (Proto → ST)
```
nanopb_generator.py (base nanoPB)
    ↓
nanopb_st_generator.py (IEC 61131 Structured Text message generator)
```

### 2. Runtime Template System (../runtime/)
```
template_engine.py (multi-platform runtime library generator)
    ↓
├── B&R (.st + .fun files)
├── CODESYS (.ST files) 
└── TwinCAT (.ST files)
```

## 🎯 Current Status

### ✅ **Completed Components**
- **nanopb_st_generator.py** - Fully functional proto-to-ST message generator
- **../runtime/template_engine.py** - Multi-platform runtime library generator
- **B&R Automation Support** - Complete B&R Automation Studio integration

### 🚧 **In Progress Components**
- CODESYS Support
- TwinCAT Support

### 📋 **Planned Components**
- Siemens AX 

## 📦 Current Components

### `nanopb_st_generator.py`
**Main ST Generator** 
- Protocol Buffer to IEC 61131-3 conversion
- Extends nanoPB generator with ST-specific functionality using composition pattern
- Generates message structures, descriptor arrays, and helper functions
- Supports all major protobuf features (nested messages, repeated fields, enumerations)
- Multi-platform output with proper type mapping and syntax
- Handles B&R, CODESYS, and TwinCAT platform differences

**Key Features:**
- **Multi-Platform Support**: Generates code for B&R, CODESYS, and TwinCAT
- **Complete Type System**: Maps all protobuf types to appropriate ST equivalents
- **Descriptor Generation**: Creates nanoPB-compatible field descriptors in ST

### Runtime Library System (`../runtime/`)

#### `template_engine.py`
**Multi-Platform Runtime Generator** - Generates nanoPB runtime libraries
- Processes templates with platform-specific token replacement
- Generates complete runtime libraries for encode/decode operations
- Handles platform-specific type mappings and function signatures

#### `function_parser.py`  
**Function Signature Processor** - B&R-specific function handling
- Strips VAR sections from B&R .st files (implementation only)
- Maintains complete function declarations in .fun files
- Handles return type removal for B&R function syntax compliance
- Processes templates with proper VAR section management

#### Platform Templates
- **pb_codec**: Main encode/decode functions
- **pb_fields**: Field processing and validation
- **pb_iterator**: Message field iteration  
- **pb_stream**: Stream I/O operations
- **pb_varint**: Variable-length integer encoding/decoding
- **Constants/Types**: Platform-specific type definitions and constants

## 🚀 Usage

### Message Code Generation
```bash
# Generate ST message code from proto file (main generator)
cd iec61131/generator
python nanopb_st_generator.py ../examples/iot_sensors.proto ./generated/ --platform br

# Generate for all platforms
python nanopb_st_generator.py ../examples/iot_sensors.proto ./generated/ --platform br
python nanopb_st_generator.py ../examples/iot_sensors.proto ./generated/ --platform codesys  
python nanopb_st_generator.py ../examples/iot_sensors.proto ./generated/ --platform twincat
```

### Runtime Library Generation
```bash
# Generate runtime libraries for all platforms
cd iec61131/runtime
python template_engine.py --clean

# Generate for specific platform
python template_engine.py --platform br --clean
python template_engine.py --platform codesys --clean
python template_engine.py --platform twincat --clean
```

### Complete Project Setup
```bash
# Full project generation workflow
cd iec61131

# 1. Generate runtime libraries
python runtime/template_engine.py --clean

# 2. Generate message code  
python generator/nanopb_st_generator.py examples/iot_sensors.proto ./generated/ --platform br

# 3. Import generated libraries into your automation project
```

### Command Line Options

#### nanopb_st_generator.py
```bash
python nanopb_st_generator.py <proto_file> <output_dir> [options]

Arguments:
  proto_file              Input .proto file to process
  output_dir              Directory for generated ST code

Options:
  --platform {br,codesys,twincat}    Target platform (default: br)
  --library-name NAME                Generated library name (default: from proto)
  --max-string-length SIZE          Maximum string length (default: 256) 
  --max-array-size SIZE             Maximum array size (default: 100)
  --debug                           Enable debug output
```

#### template_engine.py  
```bash
python template_engine.py [options]

Options:
  --platform {br,codesys,twincat,all}   Target platform(s) (default: all)
  --clean                               Clean previous generated files
  --output-dir DIR                      Override output directory
  --verbose                             Enable verbose output
```

## 🔄 Generation Process

### Message Generation Workflow (nanopb_st_generator.py)

#### 1. Protocol Buffer Parsing
- Parses `.proto` files using nanoPB's protobuf parser
- Extracts message definitions, fields, enums, and metadata  
- Resolves imports and dependencies
- Validates protobuf syntax and semantics

#### 2. ST Type System Mapping
**Comprehensive Type Translation:**
```
Protocol Buffer → ST Type Mapping
├── int32, sint32      → DINT
├── int64, sint64      → pb_int64_struct  
├── uint32             → UDINT
├── uint64             → pb_uint64_struct
├── float              → REAL
├── double             → LREAL
├── bool               → BOOL
├── string             → STRING[n]
├── bytes              → ARRAY[0..n] OF USINT
├── enum               → Custom ENUM type
└── message            → Custom STRUCT type
```

#### 3. Code Structure Generation
- **Message Structures**: ST STRUCT definitions with proper field types
- **Field Descriptors**: nanoPB-compatible descriptor arrays for runtime
- **Helper Functions**: Platform-specific encode/decode utilities
- **Constants**: Message tags, field counts, size limits
- **Library Metadata**: Platform-specific library definition files

#### 4. Platform-Specific Output

##### B&R Automation Studio
```
generated/MyProto/
├── MyProto.lby          # Library definition
├── Types.typ            # Message type definitions
├── Constants.var        # Field descriptors and constants  
└── README.md           # Generated documentation
```

##### CODESYS/TwinCAT
```
generated/MyProto/
├── MyProto.library      # Library definition
├── Types.DUT            # Data Unit Types (message structures)
├── Constants.GVL        # Global variable list (descriptors)
└── README.md           # Generated documentation
```

### Runtime Library Generation (../runtime/template_engine.py)

#### 1. Template Processing
- Processes function templates with platform-specific tokens
- Replaces type placeholders with platform-appropriate types
- Handles conditional compilation for platform differences
- Generates complete function implementations

#### 2. Multi-Platform Generation
- **B&R**: Dual-file architecture (.st + .fun) for Automation Studio compliance
- **CODESYS**: Single .ST files with inline declarations  
- **TwinCAT**: Single .ST files optimized for TwinCAT compiler
- **Token Replacement**: Platform-specific type mapping and function signatures

#### 3. Function Library Structure
**Generated Runtime Functions:**
- **Encoding Functions**: `pb_st_encode()`, `pb_st_encode_field()`
- **Decoding Functions**: `pb_st_decode()`, `pb_st_decode_field()`  
- **Stream Operations**: `pb_st_read()`, `pb_st_write()`, substream handling
- **Varint Operations**: Variable-length integer encoding/decoding
- **Field Processing**: Field iteration, validation, and type checking

### File Content Details

#### Generated Message Files
- **`.typ/.DUT`** - Complete message structures with:
  - All message fields with appropriate ST types
  - Optional field flags (`has_fieldname`) 
  - Nested message support
  - Enumeration definitions
  
- **`.var/.GVL`** - Field descriptor arrays containing:
  - Field tags, types, and offsets  
  - Message size calculations
  - Field count constants
  - Platform-specific descriptor format

- **`.lby/.library`** - Library metadata with:
  - Dependencies on runtime library
  - Library version and description
  - Platform-specific library settings

#### Runtime Library Files (B&R Architecture)
- **`.fun`** - Function declarations with return types and VAR sections
  ```st
  FUNCTION pb_st_encode : BOOL (* Encode message *)
    VAR_INPUT
      stream : pb_ostream_struct;
      fields : pb_msgdesc_struct;
      src_struct : UDINT;
    END_VAR
  END_FUNCTION
  ```

- **`.st`** - Implementation without VAR sections or return types  
  ```st
  FUNCTION pb_st_encode (* Encode message *)
    (* Implementation code here *)
    pb_st_encode := success;
  END_FUNCTION
  ```

## 🧪 Testing & Validation

### Integration Testing
```bash
# Test complete workflow with sample proto
cd iec61131

# 1. Generate runtime libraries  
python runtime/template_engine.py --platform br --clean

# 2. Generate message code from sample
python generator/nanopb_st_generator.py examples/iot_sensors.proto ./test_generated/ --platform br

# 3. Verify generated file structure
ls ./test_generated/
ls ./runtime/generated/br/
```

### Platform Validation
```bash  
# Test all platform outputs
python runtime/template_engine.py --clean  # Generates for all platforms
python generator/nanopb_st_generator.py examples/iot_sensors.proto ./test_multi/ --platform br
python generator/nanopb_st_generator.py examples/iot_sensors.proto ./test_multi/ --platform codesys
python generator/nanopb_st_generator.py examples/iot_sensors.proto ./test_multi/ --platform twincat
```

## 📚 API Reference

### nanopb_st_generator.py

#### Main Classes

**`STGenerator`** - Main generator class
- `generate(proto_file, output_dir, platform)` - Generate ST code from proto
- `generate_message_types(messages)` - Generate message structures  
- `generate_field_descriptors(messages)` - Generate nanoPB descriptors
- `get_platform_config(platform)` - Get platform-specific settings

**`MessageConverter`** - Message-specific conversion
- `convert_message_to_struct(message)` - Convert protobuf message to ST struct
- `generate_field_declarations(fields)` - Generate struct field definitions
- `handle_nested_types(message)` - Process nested messages and enums

**`PlatformWriter`** - Platform-specific file generation  
- `write_br_library(library_data)` - Generate B&R library package
- `write_codesys_library(library_data)` - Generate CODESYS library package
- `write_twincat_library(library_data)` - Generate TwinCAT library package

#### Key Methods

```python
# Generate complete ST library from proto file
generator = STGenerator()
generator.generate("sensor.proto", "./output/", "br")

# Platform-specific type mapping
st_type = generator.get_st_type("int32", "br")  # Returns "DINT"

# Custom message processing
message_struct = generator.convert_message_to_struct(proto_message)
```

### template_engine.py  

#### Main Classes

**`TemplateEngine`** - Multi-platform runtime generation
- `generate_all_platforms()` - Generate runtime for all platforms
- `generate_platform(platform_name)` - Generate for specific platform
- `clean_generated_files()` - Clean previous output

**`FunctionProcessor`** - Function template processing
- `process_template(template, tokens)` - Apply token replacement
- `strip_var_sections(content)` - Remove VAR sections for B&R .st files
- `generate_fun_declarations(functions)` - Generate .fun file content

## 🔍 Troubleshooting

### Common Issues & Solutions

#### Generation Issues

**"Unknown platform specified"**
```bash  
# Solution: Use supported platforms
python nanopb_st_generator.py file.proto ./output/ --platform br      # ✅ Supported
python nanopb_st_generator.py file.proto ./output/ --platform codesys # ✅ Supported  
python nanopb_st_generator.py file.proto ./output/ --platform twincat # ✅ Supported
python nanopb_st_generator.py file.proto ./output/ --platform invalid # ❌ Not supported
```

**"Template processing failed"**
```bash
# Solution: Ensure runtime templates exist and are valid
ls ../runtime/templates/  # Should show template files
python ../runtime/template_engine.py --clean  # Regenerate runtime libraries
```

```bash
# Enable debug output for detailed generation information
python nanopb_st_generator.py file.proto ./output/ --platform br --debug

# Enable verbose output for runtime generation  
python template_engine.py --platform br --verbose
```

#### Development Setup
```bash
# Clone repository
git clone https://github.com/Joshpolansky/nanopb_ST.git
cd nanopb_ST

# Set up development environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

#### Adding New Platform Support
```python
# 1. Add platform configuration to nanopb_st_generator.py
PLATFORM_CONFIGS = {
    'new_platform': {
        'file_extensions': {
            'types': '.XYZ',
            'variables': '.ABC', 
            'library': '.DEF'
        },
        'type_mapping': {
            'DINT': 'INT32_TYPE',
            'REAL': 'FLOAT_TYPE',
            # ... platform-specific mappings
        }
    }
}

# 2. Add templates to runtime/templates/ with platform tokens
# 3. Update template_engine.py with new platform configuration  
# 4. Add comprehensive tests and documentation
```

### Community & Support

#### Getting Help
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share experiences
- **Wiki**: Comprehensive documentation and examples
- **Examples**: Sample projects and use cases

#### Feedback & Feature Requests
We welcome feedback on:
- Generated code quality and efficiency
- Platform-specific improvements
- New platform support requests  
- Documentation and usability enhancements
- Integration with automation development workflows

---

## 📄 License & Credits

This project extends the [nanoPB Protocol Buffers library](https://github.com/nanopb/nanopb) for IEC 61131-3 Structured Text environments.

**nanoPB License**: [Zlib License](https://github.com/nanopb/nanopb/blob/master/LICENSE.txt)  
**nanoPB-ST Extensions**: MIT License

### Acknowledgments
- **nanoPB Team**: For the excellent Protocol Buffers C library foundation
