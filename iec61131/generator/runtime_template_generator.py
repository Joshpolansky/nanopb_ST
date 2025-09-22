#!/usr/bin/env python3

"""
nanoPB Runtime Library Template Generator
Generates platform-specific runtime libraries from common templates
"""

import os
import re
from typing import Dict, List, Any
from pathlib import Path


class PlatformRuntimeConfig:
    """Configuration for platform-specific runtime generation"""
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.file_extensions = {}
        self.memory_functions = {}
        self.pointer_syntax = {}
        self.type_mappings = {}
        self.library_structure = {}
        self.platform_includes = []
        self.syntax_replacements = {}


class BRRuntimeConfig(PlatformRuntimeConfig):
    """B&R Automation Studio runtime configuration"""
    
    def __init__(self):
        super().__init__("br")
        self.file_extensions = {
            "types": ".typ",
            "variables": ".var", 
            "code": ".st",
            "functions": ".fun",
            "library": ".lby"
        }
        self.memory_functions = {
            "memcpy": "brsmemcpy",
            "memset": "brsmemset",
            "strlen": "brsstrlen"
        }
        self.pointer_syntax = {
            "access_pattern": r"(\w+)\s+ACCESS\s+(.+)",
            "access_replacement": r"\1 ACCESS \2",
            "dereference": "ACCESS"
        }
        self.type_mappings = {
            "pb_byte_t": "USINT",
            "pb_size_t": "UINT", 
            "pb_ssize_t": "INT",
            "pb_type_t": "USINT"
        }
        self.library_structure = {
            "has_library_file": True,
            "library_template": "br_library_template.lby",
            "function_declarations": True
        }
        self.platform_includes = [
            "#include <brsystem.h>",
            "#include <string.h>"
        ]


class CodesysRuntimeConfig(PlatformRuntimeConfig):
    """Codesys runtime configuration"""
    
    def __init__(self):
        super().__init__("codesys")
        self.file_extensions = {
            "types": ".DUT",
            "variables": ".GVL",
            "code": ".ST", 
            "functions": ".EXP",
            "library": ".library"
        }
        self.memory_functions = {
            "memcpy": "MEMCPY",
            "memset": "MEMSET", 
            "strlen": "LEN"
        }
        self.pointer_syntax = {
            "access_pattern": r"(\w+)\s+ACCESS\s+(.+)",
            "access_replacement": r"\1^ := ADR(\2^)",
            "dereference": "^"
        }
        self.type_mappings = {
            "pb_byte_t": "USINT",
            "pb_size_t": "UINT",
            "pb_ssize_t": "INT", 
            "pb_type_t": "USINT"
        }
        self.library_structure = {
            "has_library_file": True,
            "library_template": "codesys_library_template.library",
            "function_declarations": False  # Functions declared inline
        }
        self.syntax_replacements = {
            "VAR_CONSTANT": "VAR_GLOBAL CONSTANT",
            "VAR": "VAR_GLOBAL"
        }


class TwinCATRuntimeConfig(PlatformRuntimeConfig):
    """TwinCAT runtime configuration"""
    
    def __init__(self):
        super().__init__("twincat")
        self.file_extensions = {
            "types": ".DUT",
            "variables": ".GVL",
            "code": ".ST",
            "functions": ".EXP", 
            "library": ".library"
        }
        self.memory_functions = {
            "memcpy": "MEMCPY",
            "memset": "MEMSET",
            "strlen": "LEN"
        }
        self.pointer_syntax = {
            "access_pattern": r"(\w+)\s+ACCESS\s+(.+)",
            "access_replacement": r"\1 := \2",
            "dereference": ""  # TwinCAT may handle differently
        }
        self.type_mappings = {
            "pb_byte_t": "BYTE",
            "pb_size_t": "UINT",
            "pb_ssize_t": "INT",
            "pb_type_t": "USINT"
        }
        self.library_structure = {
            "has_library_file": True,
            "library_template": "twincat_library_template.library",
            "function_declarations": False
        }
        self.syntax_replacements = {
            "VAR_CONSTANT": "VAR_GLOBAL CONSTANT", 
            "VAR": "VAR_GLOBAL"
        }


class RuntimeTemplateEngine:
    """Template engine for generating platform-specific runtime libraries"""
    
    def __init__(self, source_runtime_path: str):
        self.source_path = Path(source_runtime_path)
        self.templates = {}
        self.load_templates()
    
    def load_templates(self):
        """Load all source runtime files as templates"""
        if not self.source_path.exists():
            raise FileNotFoundError(f"Source runtime path not found: {self.source_path}")
        
        for file_path in self.source_path.glob("*"):
            if file_path.is_file():
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.templates[file_path.name] = f.read()
    
    def apply_platform_config(self, content: str, config: PlatformRuntimeConfig) -> str:
        """Apply platform-specific replacements to template content"""
        
        # Apply memory function replacements
        for generic_func, platform_func in config.memory_functions.items():
            pattern = rf'\b{generic_func}\b'
            content = re.sub(pattern, platform_func, content)
        
        # Apply pointer syntax replacements
        if config.pointer_syntax.get("access_pattern"):
            pattern = config.pointer_syntax["access_pattern"]
            replacement = config.pointer_syntax["access_replacement"]
            content = re.sub(pattern, replacement, content)
        
        # Apply type mappings
        for generic_type, platform_type in config.type_mappings.items():
            pattern = rf'\b{generic_type}\b'
            content = re.sub(pattern, platform_type, content)
        
        # Apply syntax replacements
        for old_syntax, new_syntax in config.syntax_replacements.items():
            content = content.replace(old_syntax, new_syntax)
        
        # Add platform-specific header
        header = f"""(* nanoPB Runtime Library for {config.platform_name.upper()} *)
(* Generated from template - DO NOT EDIT MANUALLY *)
(* Platform: {config.platform_name} *)

"""
        content = header + content
        
        return content
    
    def generate_platform_runtime(self, config: PlatformRuntimeConfig, output_path: str) -> List[str]:
        """Generate complete runtime library for specified platform"""
        
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        generated_files = []
        
        # File extension mapping
        extension_map = {
            ".typ": config.file_extensions["types"],
            ".var": config.file_extensions["variables"],
            ".st": config.file_extensions["code"],
            ".fun": config.file_extensions.get("functions", ".EXP"),
            ".lby": config.file_extensions.get("library", ".library")
        }
        
        for template_name, template_content in self.templates.items():
            # Skip README and other non-code files
            if template_name.lower() in ['readme.md', '.gitignore']:
                continue
            
            # Apply platform transformations
            transformed_content = self.apply_platform_config(template_content, config)
            
            # Determine output filename with platform-specific extension
            base_name = template_name.split('.')[0]
            original_ext = '.' + template_name.split('.', 1)[1]
            
            if original_ext in extension_map:
                output_filename = base_name + extension_map[original_ext]
            else:
                output_filename = template_name
            
            # Write platform-specific file
            output_file = output_dir / output_filename
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(transformed_content)
            
            generated_files.append(str(output_file))
        
        # Generate platform-specific library metadata
        if config.library_structure.get("has_library_file"):
            self.generate_library_metadata(config, output_dir)
            generated_files.append(str(output_dir / f"nanopb_{config.platform_name}.{config.file_extensions['library'][1:]}"))
        
        return generated_files
    
    def generate_library_metadata(self, config: PlatformRuntimeConfig, output_dir: Path):
        """Generate platform-specific library metadata files"""
        
        if config.platform_name == "br":
            # Generate B&R library file (.lby)
            library_content = f"""<?xml version="1.0" encoding="utf-8"?>
<Library xmlns="http://br-automation.co.at/AS/Library">
  <Files>
    <File>Types.typ</File>
    <File>Constants.var</File>
    <File>NanoPbSt.fun</File>
    <File>pb_stream.st</File>
    <File>pb_varint.st</File>
    <File>pb_codec.st</File>
    <File>pb_fields.st</File>
    <File>pb_iterator.st</File>
  </Files>
  <Dependencies>
    <Dependency>operator</Dependency>
    <Dependency>runtime</Dependency>
    <Dependency>string_utils</Dependency>
  </Dependencies>
</Library>"""
        
        elif config.platform_name == "codesys":
            # Generate Codesys library info
            library_content = f"""(* Codesys Library Information *)
(* nanoPB Runtime Library for Codesys *)
LIBRARY_INFO
    Title: 'nanoPB Protocol Buffers'
    Version: '1.0.0'
    Author: 'nanoPB ST Generator'
    Description: 'Protocol Buffers runtime for Codesys'
END_LIBRARY_INFO"""
        
        elif config.platform_name == "twincat":
            # Generate TwinCAT library info
            library_content = f"""(* TwinCAT Library Information *)
(* nanoPB Runtime Library for TwinCAT *)
LIBRARY_INFO
    Title: 'nanoPB Protocol Buffers'
    Version: '1.0.0'
    Author: 'nanoPB ST Generator'  
    Description: 'Protocol Buffers runtime for TwinCAT'
END_LIBRARY_INFO"""
        
        else:
            library_content = f"(* Library info for {config.platform_name} *)"
        
        library_file = output_dir / f"nanopb_{config.platform_name}.{config.file_extensions['library'][1:]}"
        with open(library_file, 'w', encoding='utf-8') as f:
            f.write(library_content)
    
    def generate_all_platforms(self, base_output_path: str) -> Dict[str, List[str]]:
        """Generate runtime libraries for all supported platforms"""
        
        configs = {
            "br": BRRuntimeConfig(),
            "codesys": CodesysRuntimeConfig(), 
            "twincat": TwinCATRuntimeConfig()
        }
        
        results = {}
        
        for platform_name, config in configs.items():
            output_path = os.path.join(base_output_path, platform_name)
            generated_files = self.generate_platform_runtime(config, output_path)
            results[platform_name] = generated_files
            print(f"✅ Generated {platform_name} runtime library: {len(generated_files)} files")
        
        return results


def main():
    """Main function for testing the runtime template generator"""
    
    # Source B&R runtime library path
    source_runtime = os.path.abspath("../runtime/br/NanoPbSt")
    
    # Output base directory
    output_base = os.path.abspath("../runtime/generated")
    
    try:
        # Create template engine
        engine = RuntimeTemplateEngine(source_runtime)
        
        print("🏗️  Generating platform-specific runtime libraries...")
        
        # Generate all platforms
        results = engine.generate_all_platforms(output_base)
        
        print("\n📦 Generation Summary:")
        for platform, files in results.items():
            print(f"  {platform.upper()}: {len(files)} files generated")
            for file_path in files[:3]:  # Show first 3 files
                print(f"    - {Path(file_path).name}")
            if len(files) > 3:
                print(f"    ... and {len(files) - 3} more")
        
        print(f"\n✨ All runtime libraries generated successfully!")
        
    except Exception as e:
        print(f"💥 Error generating runtime libraries: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())