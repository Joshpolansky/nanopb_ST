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
            "STRLEN_FUNC": "brsstrcmp",
            # Reference/Pointer handling for B&R
            "REF_ASSIGN": "ACCESS ADR",
            "REF_DEREF": "",
            "FIELD_PTR_ACCESS": " ACCESS ",
            "ADR_FUNC": "ADR",
            "SCOPE_CONSTANT": "VAR_CONSTANT",
            "SCOPE_GLOBAL": "VAR",
            "SCOPE_LOCAL": "VAR",
            "TYPE_BYTE": "USINT",
            "TYPE_SIZE": "UINT",
            "TYPE_SSIZE": "INT",
            "TYPE_TYPE": "USINT",
            "PLATFORM_NAME": "B&R",
            "PLATFORM_HEADER": "(* nanoPB Runtime Library for B&R Automation Studio *)",
            "PLATFORM_XML_HEADER": '<?AutomationStudio FileVersion="4.9"?>',
            "PLATFORM_DEPENDENCIES": '<Dependency ObjectName="AsBrStr" />',
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
        """Replace all tokens in file content"""
        processed_content = content
        for token, value in tokens.items():
            processed_content = processed_content.replace(f"{{{{{token}}}}}", value)
        return processed_content

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

        # Process each template file
        template_files = self.get_template_files()
        generated_files = []

        for template_file in template_files:
            # Read template content
            with open(template_file, "r", encoding="utf-8") as f:
                template_content = f.read()

            # Process content - replace all tokens
            processed_content = self.process_file_content(template_content, tokens)

            # Resolve output filename
            output_filename = self.resolve_filename(template_file.name, tokens)
            output_file_path = output_dir / output_filename

            # Write processed file
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write(processed_content)

            generated_files.append(output_file_path)

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
