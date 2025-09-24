#!/usr/bin/env python3
"""
nanoPB Runtime Template Engine - Simplified Token Replacement System

This system processes template files with embedded tokens and generates platform-specific runtime libraries.
Template files use tokens like {{PLATFORM_NAME}}, {{MEMCPY_FUNC}}, {{FILE_EXT_TYPES}}, etc.

The approach is much simpler than regex transformation - direct token replacement.
"""

import os
import json
import shutil
from pathlib import Path
from function_parser import FunctionProcessor


class PlatformConfig:
    """Base class for platform configurations"""

    def __init__(self):
        self.tokens = {}

    def get_token_values(self):
        """Return dictionary of token -> value mappings"""
        return self.tokens


class BRRuntimeConfig(PlatformConfig):
    """B&R Automation Studio configuration"""

    def __init__(self):
        super().__init__()
        self.tokens = {
            "FILE_EXT_TYPES": ".typ",
            "FILE_EXT_VARIABLES": ".var",
            "FILE_EXT_CODE": ".st",
            "FILE_EXT_FUNCTIONS": ".fun",
            "FILE_EXT_LIBRARY": ".lby",
            "MEMCPY_FUNC": "brsmemcpy",
            "MEMSET_FUNC": "brsmemset",
            "STRLEN_FUNC": "brsstrlen",
            # Reference/Pointer handling for B&R
            "REF_ASSIGN": "ACCESS ADR",
            "REF_DEREF": "",
            "REF_POINTER": "REFERENCE TO ",  # Note the trailing space
            "FIELD_PTR_ACCESS": " ACCESS ",
            "ADR_FUNC": "ADR",
            "PTR_TO_VOID": "UDINT",  # B&R uses UDINT for pointers
            "SCOPE_CONSTANT": "VAR CONSTANT",
            "SCOPE_GLOBAL": "VAR",
            "SCOPE_LOCAL": "VAR",
            "TYPE_BYTE": "USINT",
            "TYPE_SIZE": "UINT",
            "TYPE_SSIZE": "INT",
            "TYPE_TYPE": "USINT",
            # Data type tokens for function variables
            "PB_UINT_TYPE": "UDINT",
            "PB_INT_TYPE": "DINT", 
            "PB_WIRE_TYPE": "USINT",
            "PB_TAG_TYPE": "UINT",
            "PB_FIELD_TYPE": "USINT",
            "PB_64BIT_TYPE": "ULINT",
            "PB_STRING_TYPE": "STRING[255]",
            "PLATFORM_NAME": "B&R",
            "PLATFORM_HEADER": "(* nanoPB Runtime Library for B&R Automation Studio *)",
            "PLATFORM_XML_HEADER": '<?AutomationStudio FileVersion="4.9"?>',
            "PLATFORM_DEPENDENCIES": '<Dependency ObjectName="AsBrStr" />',
            # B&R uses .fun files for declarations - no vars in .st files
            "PB_ENCODE_VARS": "",
            "PB_DECODE_VARS": "",
            "PB_ENCODE_FIELD_VARS": "",
            "PB_DECODE_FIELD_VARS": "",
            # Type Conversions
            "UDINT_TO_UINT": "UDINT_TO_UINT",
            "UDINT_TO_USINT": "UDINT_TO_USINT",
            "UDINT_TO_SINT": "UDINT_TO_SINT",
            "UDINT_TO_BYTE": "UDINT_TO_BYTE",
            "UINT_TO_UDINT": "UINT_TO_UDINT",
            "UINT_TO_USINT": "UINT_TO_USINT",
            "USINT_TO_UDINT": "USINT_TO_UDINT",
            "SINT_TO_UDINT": "SINT_TO_UDINT",
            "DINT_TO_USINT": "DINT_TO_USINT",
            "ULINT_TO_USINT": "ARRAY_TO_USINT_COMPAT",
            "UDINT_TO_ULINT": "UDINT_TO_ARRAY_COMPAT", 
            "UINT_TO_ULINT": "UINT_TO_ARRAY_COMPAT",
            "USINT_TO_ULINT": "USINT_TO_ARRAY_COMPAT",
            "LINT_TO_ULINT": "LINT_TO_ULINT_COMPAT",
            "DINT_TO_UDINT": "DINT_TO_UDINT",
            "ULINT_TO_LINT": "ULINT_TO_LINT_COMPAT",
            "ULINT_TO_UDINT": "ARRAY_TO_UDINT_COMPAT",
            "SINT_TO_LINT": "SINT_TO_ARRAY_COMPAT",
            "INT_TO_LINT": "INT_TO_ARRAY_COMPAT", 
            "DINT_TO_LINT": "DINT_TO_ARRAY_COMPAT",
            "BOOL_TO_UDINT": "BOOL_TO_UDINT",
            "INT_TO_DINT": "INT_TO_DINT",
            "SINT_TO_DINT": "SINT_TO_DINT",
            "UDINT_TO_DINT": "UDINT_TO_DINT",
            "SINT_TO_UDINT": "SINT_TO_UDINT",
            "INT_TO_UDINT": "INT_TO_UDINT",
            "LINT_TO_UDINT": "LINT_TO_UDINT",
            # 64-bit type support - B&R does NOT support LINT/ULINT
            "SUPPORTS_64BIT": "FALSE",
            "INT64_TYPE": "ARRAY[0..1] OF DINT",  # Simulate 64-bit with array
            "UINT64_TYPE": "ARRAY[0..1] OF UDINT",  # Simulate 64-bit with array
            "UDINT_MAX_VALUE": "16#FFFFFFFF",
            "UINT_MAX_VALUE": "16#FFFF",  # Max value for UINT (16-bit)
            "SIZE_MAX_VALUE": "16#FFFF",  # For size_t fields (UINT in B&R)
            "PB_ENCODE_DELIMITED": "1",
            "PB_ENCODE_NULLTERMINATED": "2",
            "INT64_TO_UINT64": "LINT_TO_ULINT_COMPAT",
            "UINT64_TO_INT64": "ULINT_TO_LINT_COMPAT",
            # Section stripping tokens for conditional compilation
            "STRIP_64BIT_START": "{{STRIP_START}}",
            "STRIP_64BIT_END": "{{STRIP_END}}",
            "STRIP_NO64BIT_START": "",
            "STRIP_NO64BIT_END": "",
        }


class CodesysRuntimeConfig(PlatformConfig):
    """Codesys configuration"""

    def __init__(self):
        super().__init__()
        self.tokens = {
            "FILE_EXT_TYPES": ".DUT",
            "FILE_EXT_VARIABLES": ".GVL",
            "FILE_EXT_CODE": ".ST",
            "FILE_EXT_FUNCTIONS": ".EXP",
            "FILE_EXT_LIBRARY": ".library",
            "MEMCPY_FUNC": "MEMCPY",
            "MEMSET_FUNC": "MEMSET",
            "STRLEN_FUNC": "LEN",
            # Reference handling for Codesys - uses REFERENCE TO syntax
            "REF_ASSIGN": "REF=",
            "REF_DEREF": "",
            "FIELD_PTR_ACCESS": " REF= ",
            "ADR_FUNC": "ADR",
            "SCOPE_CONSTANT": "VAR_GLOBAL CONSTANT",
            "SCOPE_GLOBAL": "VAR_GLOBAL",
            "SCOPE_LOCAL": "VAR",
            "TYPE_BYTE": "USINT",
            "TYPE_SIZE": "UINT",
            "TYPE_SSIZE": "INT",
            "TYPE_TYPE": "USINT",
            "PLATFORM_NAME": "Codesys",
            "PLATFORM_HEADER": "(* nanoPB Runtime Library for Codesys *)",
            "PLATFORM_XML_HEADER": '<?xml version="1.0" encoding="utf-8"?>',
            "PLATFORM_DEPENDENCIES": "(* No special dependencies for Codesys *)",
            # Function-specific declarations for Codesys - each function needs its own vars
            "PB_ENCODE_VARS": """VAR_INPUT
        stream : pb_ostream_struct;
        fields : pb_msgdesc_struct;
        src_struct : UDINT;
    END_VAR
    VAR
        iter : pb_field_iter_struct;
        iter_ref : REFERENCE TO pb_field_iter_struct;
    END_VAR""",
            "PB_DECODE_VARS": """VAR_INPUT
        stream : pb_istream_struct;
        fields : pb_msgdesc_struct;
        dest_struct : UDINT;
    END_VAR
    VAR
        tag : UDINT;
        wire_type : pb_wire_type_t;
        tag_value : pb_size_t;
        iter : pb_field_iter_struct;
        iter_ref : REFERENCE TO pb_field_iter_struct;
        field_found : BOOL;
    END_VAR""",
            "PB_ENCODE_FIELD_VARS": """VAR_INPUT
        stream : pb_ostream_struct;
        field : pb_field_iter_struct;
    END_VAR
    VAR
        field_type : USINT;
        has_value : BOOL;
        bool_ptr : REFERENCE TO BOOL;
        int_ptr : REFERENCE TO DINT;
        uint_ptr : REFERENCE TO UDINT;
        real_ptr : REFERENCE TO REAL;
        val_64 : REFERENCE TO pb_uint64_struct;
        string_ptr : REFERENCE TO STRING[80];
    END_VAR""",
            "PB_DECODE_FIELD_VARS": """VAR_INPUT
        stream : pb_istream_struct;
        field : pb_field_iter_struct;
        wire_type : pb_wire_type_t;
    END_VAR
    VAR
        field_type : USINT;
        temp_uint : UDINT;
        bool_ptr : REFERENCE TO BOOL;
        uint_ptr : REFERENCE TO UDINT;
        int_ptr : REFERENCE TO DINT;
        val_64 : REFERENCE TO pb_uint64_struct;
        string_ptr : REFERENCE TO STRING[80];
    END_VAR""",
            # Type Conversions - Codesys
            "UDINT_TO_UINT": "UDINT_TO_UINT",
            "UDINT_TO_USINT": "UDINT_TO_USINT",
            "UDINT_TO_SINT": "UDINT_TO_SINT",
            "UDINT_TO_BYTE": "UDINT_TO_USINT",
            "UINT_TO_UDINT": "UINT_TO_UDINT",
            "UINT_TO_USINT": "UINT_TO_USINT",
            "USINT_TO_UDINT": "USINT_TO_UDINT",
            "SINT_TO_UDINT": "SINT_TO_UDINT",
            "ULINT_TO_USINT": "ULINT_TO_USINT",
            "UDINT_TO_ULINT": "UDINT_TO_ULINT",
            "UINT_TO_ULINT": "UINT_TO_ULINT",
            "USINT_TO_ULINT": "USINT_TO_ULINT",
            "LINT_TO_ULINT": "LINT_TO_ULINT",
            "ULINT_TO_LINT": "ULINT_TO_LINT",
            "ULINT_TO_UDINT": "ULINT_TO_UDINT",
            "SINT_TO_LINT": "SINT_TO_LINT",
            "INT_TO_LINT": "INT_TO_LINT",
            "DINT_TO_LINT": "DINT_TO_LINT",
            "SINT_TO_UDINT": "SINT_TO_UDINT",
            "INT_TO_UDINT": "INT_TO_UDINT",
            "LINT_TO_UDINT": "LINT_TO_UDINT",
            "DINT_TO_UDINT": "DINT_TO_UDINT",
            "SINT_TO_DINT": "SINT_TO_DINT",
            "INT_TO_DINT": "INT_TO_DINT",
            # 64-bit type support - Codesys supports LINT/ULINT
            "SUPPORTS_64BIT": "TRUE",
            "INT64_TYPE": "LINT",
            "UINT64_TYPE": "ULINT",
            "UDINT_MAX_VALUE": "16#FFFFFFFF",
            "INT64_TO_UINT64": "LINT_TO_ULINT",
            "UINT64_TO_INT64": "ULINT_TO_LINT",
            # Section stripping tokens for conditional compilation
            "STRIP_64BIT_START": "",
            "STRIP_64BIT_END": "",
            "STRIP_NO64BIT_START": "{{STRIP_START}}",
            "STRIP_NO64BIT_END": "{{STRIP_END}}",
        }


class TwinCATRuntimeConfig(PlatformConfig):
    """TwinCAT configuration"""

    def __init__(self):
        super().__init__()
        self.tokens = {
            "FILE_EXT_TYPES": ".DUT",
            "FILE_EXT_VARIABLES": ".GVL",
            "FILE_EXT_CODE": ".ST",
            "FILE_EXT_FUNCTIONS": ".EXP",
            "FILE_EXT_LIBRARY": ".library",
            "MEMCPY_FUNC": "MEMCPY",
            "MEMSET_FUNC": "MEMSET",
            "STRLEN_FUNC": "LEN",
            # Reference handling for TwinCAT - similar to Codesys
            "REF_ASSIGN": "REF=",
            "REF_DEREF": "",
            "FIELD_PTR_ACCESS": " REF= ",
            "ADR_FUNC": "ADR",
            "SCOPE_CONSTANT": "VAR_GLOBAL CONSTANT",
            "SCOPE_GLOBAL": "VAR_GLOBAL",
            "SCOPE_LOCAL": "VAR",
            "TYPE_BYTE": "BYTE",
            "TYPE_SIZE": "UINT",
            "TYPE_SSIZE": "INT",
            "TYPE_TYPE": "USINT",
            "PLATFORM_NAME": "TwinCAT",
            "PLATFORM_HEADER": "(* nanoPB Runtime Library for TwinCAT *)",
            "PLATFORM_XML_HEADER": '<?xml version="1.0" encoding="utf-8"?>',
            "PLATFORM_DEPENDENCIES": "(* No special dependencies for TwinCAT *)",
            # Function-specific declarations for TwinCAT - each function needs its own vars
            "PB_ENCODE_VARS": """VAR_INPUT
        stream : pb_ostream_struct;
        fields : pb_msgdesc_struct;
        src_struct : UDINT;
    END_VAR
    VAR
        iter : pb_field_iter_struct;
        iter_ref : REFERENCE TO pb_field_iter_struct;
    END_VAR""",
            "PB_DECODE_VARS": """VAR_INPUT
        stream : pb_istream_struct;
        fields : pb_msgdesc_struct;
        dest_struct : UDINT;
    END_VAR
    VAR
        tag : UDINT;
        wire_type : pb_wire_type_t;
        tag_value : pb_size_t;
        iter : pb_field_iter_struct;
        iter_ref : REFERENCE TO pb_field_iter_struct;
        field_found : BOOL;
    END_VAR""",
            "PB_ENCODE_FIELD_VARS": """VAR_INPUT
        stream : pb_ostream_struct;
        field : pb_field_iter_struct;
    END_VAR
    VAR
        field_type : BYTE;
        has_value : BOOL;
        bool_ptr : REFERENCE TO BOOL;
        int_ptr : REFERENCE TO DINT;
        uint_ptr : REFERENCE TO UDINT;
        real_ptr : REFERENCE TO REAL;
        val_64 : REFERENCE TO pb_uint64_struct;
        string_ptr : REFERENCE TO STRING[80];
    END_VAR""",
            "PB_DECODE_FIELD_VARS": """VAR_INPUT
        stream : pb_istream_struct;
        field : pb_field_iter_struct;
        wire_type : pb_wire_type_t;
    END_VAR
    VAR
        field_type : BYTE;
        temp_uint : UDINT;
        bool_ptr : REFERENCE TO BOOL;
        uint_ptr : REFERENCE TO UDINT;
        int_ptr : REFERENCE TO DINT;
        val_64 : REFERENCE TO pb_uint64_struct;
        string_ptr : REFERENCE TO STRING[80];
    END_VAR""",
            # Type Conversions - TwinCAT
            "UDINT_TO_UINT": "UDINT_TO_UINT",
            "UDINT_TO_USINT": "UDINT_TO_USINT",
            "UDINT_TO_SINT": "UDINT_TO_SINT",
            "UDINT_TO_BYTE": "UDINT_TO_BYTE",
            "UINT_TO_UDINT": "UINT_TO_UDINT",
            "UINT_TO_USINT": "UINT_TO_USINT",
            "USINT_TO_UDINT": "USINT_TO_UDINT",
            "SINT_TO_UDINT": "SINT_TO_UDINT",
            "ULINT_TO_USINT": "ULINT_TO_USINT",
            "UDINT_TO_ULINT": "UDINT_TO_ULINT",
            "UINT_TO_ULINT": "UINT_TO_ULINT",
            "USINT_TO_ULINT": "USINT_TO_ULINT",
            "LINT_TO_ULINT": "LINT_TO_ULINT",
            "ULINT_TO_LINT": "ULINT_TO_LINT",
            "ULINT_TO_UDINT": "ULINT_TO_UDINT",
            "SINT_TO_LINT": "SINT_TO_LINT",
            "INT_TO_LINT": "INT_TO_LINT",
            "DINT_TO_LINT": "DINT_TO_LINT",
            "SINT_TO_UDINT": "SINT_TO_UDINT",
            "INT_TO_UDINT": "INT_TO_UDINT",
            "LINT_TO_UDINT": "LINT_TO_UDINT",
            "DINT_TO_UDINT": "DINT_TO_UDINT",
            "SINT_TO_DINT": "SINT_TO_DINT",
            "INT_TO_DINT": "INT_TO_DINT",
            # 64-bit type support - TwinCAT supports LINT/ULINT
            "SUPPORTS_64BIT": "TRUE", 
            "INT64_TYPE": "LINT",
            "UINT64_TYPE": "ULINT",
            "UDINT_MAX_VALUE": "16#FFFFFFFF",
            "LINT_TO_ULINT": "LINT_TO_ULINT",
            "ULINT_TO_LINT": "ULINT_TO_LINT",
            "USINT_TO_ULINT": "USINT_TO_ULINT",
            "ULINT_TO_UDINT": "ULINT_TO_UDINT",
            "ULINT_TO_USINT": "ULINT_TO_USINT",
            "INT64_TO_UINT64": "LINT_TO_ULINT",
            "UINT64_TO_INT64": "ULINT_TO_LINT",
            # Section stripping tokens for conditional compilation
            "STRIP_64BIT_START": "",
            "STRIP_64BIT_END": "",
            "STRIP_NO64BIT_START": "{{STRIP_START}}",
            "STRIP_NO64BIT_END": "{{STRIP_END}}",
        }


class RuntimeTemplateEngine:
    """Engine for processing runtime library templates"""

    def __init__(self, workspace_root):
        self.workspace_root = Path(workspace_root)
        self.template_dir = self.workspace_root / "iec61131" / "runtime" / "templates"
        self.output_base_dir = self.workspace_root / "iec61131" / "runtime" / "generated"

        # Platform configurations
        self.platforms = {
            "br": BRRuntimeConfig(),
            "codesys": CodesysRuntimeConfig(),
            "twincat": TwinCATRuntimeConfig(),
        }

    def get_template_files(self):
        """Get all template files with token-based names"""
        template_files = []
        if self.template_dir.exists():
            for file_path in self.template_dir.iterdir():
                if file_path.is_file() and "{{" in file_path.name:
                    template_files.append(file_path)
        return template_files

    def resolve_filename(self, template_filename, tokens):
        """Resolve template tokens in filename"""
        resolved_name = template_filename
        for token, value in tokens.items():
            resolved_name = resolved_name.replace(f"{{{{{token}}}}}", value)
        return resolved_name

    def process_file_content(self, content, tokens):
        """Replace all tokens in file content and strip marked sections"""
        # First, replace all regular tokens
        processed_content = content
        for token, value in tokens.items():
            processed_content = processed_content.replace(f"{{{{{token}}}}}", value)
        
        # Then strip marked sections
        processed_content = self.strip_marked_sections(processed_content)
        
        return processed_content
    
    def strip_marked_sections(self, content):
        """Remove sections marked with {{STRIP_START}} ... {{STRIP_END}}"""
        import re
        
        # Remove all sections marked for stripping
        pattern = r'\{\{STRIP_START\}\}.*?\{\{STRIP_END\}\}'
        content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        # Clean up extra blank lines that might be left after stripping
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        return content

    def clean_generated_files(self):
        """Clean up previously generated files"""
        if self.output_base_dir.exists():
            print(f"🧹 Cleaning up previous generated files in {self.output_base_dir}")
            shutil.rmtree(self.output_base_dir)
        self.output_base_dir.mkdir(parents=True, exist_ok=True)

    def generate_platform_library(self, platform_name):
        """Generate runtime library for a specific platform"""
        if platform_name not in self.platforms:
            raise ValueError(f"Unknown platform: {platform_name}")

        config = self.platforms[platform_name]
        tokens = config.get_token_values()

        # Create output directory
        output_dir = self.output_base_dir / platform_name / "NanoPbSt"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize function processor for VAR section handling
        processor = FunctionProcessor()

        # Process each template file
        template_files = self.get_template_files()
        generated_files = []
        
        # For B&R, collect all function declarations in a single .fun file
        if platform_name.lower() == 'br':
            consolidated_fun_content = []
            consolidated_fun_content.append(tokens.get("PLATFORM_HEADER", ""))
            consolidated_fun_content.append("(* nanoPB library function declarations for B&R Automation Studio *)")
            consolidated_fun_content.append("")

        for template_file in template_files:
            # Read template content
            with open(template_file, "r", encoding="utf-8") as f:
                template_content = f.read()

            # Special handling for function templates (those containing {{FILE_EXT_CODE}})
            if "{{FILE_EXT_CODE}}" in template_file.name:
                print(f"   🔧 Processing function template: {template_file.name}")
                
                # For B&R platform, generate .st files and collect .fun content
                if platform_name.lower() == 'br':
                    # Process tokens first to handle conditional compilation
                    processed_template = self.process_file_content(template_content, tokens)
                    
                    # Generate .st file with VAR sections stripped
                    st_content = processor.strip_var_sections(processed_template)
                    
                    # Add function declarations to consolidated .fun content
                    fun_content = processor.generate_fun_from_template(processed_template, tokens)
                    # Extract just the function declarations (skip header)
                    fun_lines = fun_content.split('\n')
                    in_header = True
                    for line in fun_lines:
                        if line.strip().startswith('FUNCTION'):
                            in_header = False
                        if not in_header:
                            consolidated_fun_content.append(line)
                    
                    # Write .st file only (no individual .fun file)
                    st_filename = self.resolve_filename(template_file.name, tokens)
                    st_path = output_dir / st_filename
                    with open(st_path, "w", encoding="utf-8") as f:
                        f.write(st_content)
                    generated_files.append(st_path)
                    
                else:
                    # For Codesys/TwinCAT, use complete template with VAR sections
                    processed_content = self.process_file_content(template_content, tokens)
                    output_filename = self.resolve_filename(template_file.name, tokens)
                    output_file_path = output_dir / output_filename
                    
                    with open(output_file_path, "w", encoding="utf-8") as f:
                        f.write(processed_content)
                    generated_files.append(output_file_path)
                    
            elif "{{FILE_EXT_FUNCTIONS}}" in template_file.name and platform_name.lower() == 'br':
                # For B&R, skip the NanoPbSt.fun template - we'll generate our own consolidated version
                continue
                    
            else:
                # Regular template processing for non-function files
                processed_content = self.process_file_content(template_content, tokens)
                output_filename = self.resolve_filename(template_file.name, tokens)
                output_file_path = output_dir / output_filename

                with open(output_file_path, "w", encoding="utf-8") as f:
                    f.write(processed_content)
                generated_files.append(output_file_path)

        # For B&R, write the consolidated .fun file (replacing the template-based one)
        if platform_name.lower() == 'br':
            consolidated_fun_processed = self.process_file_content('\n'.join(consolidated_fun_content), tokens)
            fun_path = output_dir / "NanoPbSt.fun"
            with open(fun_path, "w", encoding="utf-8") as f:
                f.write(consolidated_fun_processed)
            generated_files.append(fun_path)

        return generated_files

    def generate_all_platforms(self):
        """Generate runtime libraries for all platforms"""
        results = {}

        for platform_name in self.platforms.keys():
            try:
                generated_files = self.generate_platform_library(platform_name)
                results[platform_name] = {
                    "success": True,
                    "files": generated_files,
                    "count": len(generated_files),
                }
                print(
                    f"✅ {platform_name.upper()}: Generated {len(generated_files)} files"
                )
                for file_path in generated_files:
                    print(f"   📄 {file_path}")

            except Exception as e:
                results[platform_name] = {"success": False, "error": str(e), "count": 0}
                print(f"❌ {platform_name.upper()}: Failed - {e}")

        return results

    def validate_templates(self):
        """Validate that template files exist and have proper token syntax"""
        template_files = self.get_template_files()

        if not template_files:
            print("⚠️ No template files found in", self.template_dir)
            return False

        print(f"📋 Found {len(template_files)} template files:")
        for template_file in template_files:
            print(f"   📄 {template_file.name}")

        return True


def main():
    """Main execution function"""
    workspace_root = r"E:\clients\br\nanopb_ST"

    print("🔄 Starting nanoPB Runtime Template Engine (Token-Based)")
    print(f"📁 Workspace: {workspace_root}")

    # Initialize engine
    engine = RuntimeTemplateEngine(workspace_root)

    # Validate templates
    if not engine.validate_templates():
        print("❌ Template validation failed")
        return

    print("\n🏗️ Generating platform-specific runtime libraries...")

    # Clean up previous generated files
    engine.clean_generated_files()

    # Generate all platforms
    results = engine.generate_all_platforms()

    # Summary
    print("\n📊 Generation Summary:")
    total_files = 0
    successful_platforms = 0

    for platform, result in results.items():
        if result["success"]:
            successful_platforms += 1
            total_files += result["count"]
            print(f"   ✅ {platform.upper()}: {result['count']} files")
        else:
            print(f"   ❌ {platform.upper()}: {result['error']}")

    print(
        f"\n🎯 Results: {successful_platforms}/{len(results)} platforms successful, {total_files} files generated"
    )
    print(f"📁 Generated files location: {engine.output_base_dir}")


if __name__ == "__main__":
    main()
