#!/usr/bin/env python3
"""
Function Declaration Parser for nanoPB Runtime Templates

Parses complete function implementations to:
- Extract VAR sections for B&R .fun file generation
- Strip VAR sections for B&R .st file generation
- Keep complete functions for Codesys/TwinCAT

This approach keeps declarations WITH implementations in templates.
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple


@dataclass
class Parameter:
    """Represents a function parameter or variable"""

    name: str
    type: str
    comment: Optional[str] = None


@dataclass
class FunctionDeclaration:
    """Complete function declaration info"""

    name: str
    return_type: str
    inputs: List[Parameter]
    outputs: List[Parameter]
    in_out: List[Parameter]
    locals: List[Parameter]
    description: Optional[str] = None
    group: Optional[str] = None
    category: Optional[str] = None


class FunctionProcessor:
    """Processes function templates for platform-specific output"""

    def __init__(self):
        # Regex patterns for parsing function declarations
        self.function_header_pattern = (
            r"FUNCTION\s+(\w+)(?:\s*:\s*(\w+))?\s*(?:\([^)]*\))?\s*(?:\(\*([^)]*)\*\))?"
        )
        self.var_section_pattern = r"(VAR(?:_INPUT|_OUTPUT|_IN_OUT)\s*.*?\s*END_VAR)"
        self.var_content_pattern = r"VAR(?:_INPUT|_OUTPUT|_IN_OUT)\s*(.*?)\s*END_VAR"

    def extract_function_declarations(
        self, template_content: str
    ) -> Dict[str, FunctionDeclaration]:
        """
        Extract function declarations from template content

        Args:
            template_content: Complete template with functions including VAR sections

        Returns:
            Dictionary mapping function names to their declarations
        """
        functions = {}

        # Find all function blocks
        function_blocks = self._find_function_blocks(template_content)

        for block in function_blocks:
            try:
                declaration = self._parse_function_declaration(block)
                if declaration:
                    functions[declaration.name] = declaration
            except Exception as e:
                print(f"Warning: Failed to parse function: {e}")
                continue

        return functions

    def strip_var_sections(self, template_content: str) -> str:
        """
        Strip VAR sections and return types from template content for B&R .st files

        Args:
            template_content: Complete template with VAR sections

        Returns:
            Template content with VAR sections removed and return types stripped from function signatures
        """
        # Remove all VAR sections (VAR, VAR_INPUT, VAR_OUTPUT, VAR_IN_OUT) using a simpler approach
        # Split by lines, filter out VAR blocks, and rejoin
        lines = template_content.split("\n")
        result_lines = []
        in_var_block = False

        for line in lines:
            stripped = line.strip().upper()

            # Check if we're entering a VAR block
            if stripped.startswith("VAR") and (
                stripped == "VAR"
                or stripped.startswith("VAR_INPUT")
                or stripped.startswith("VAR_OUTPUT")
                or stripped.startswith("VAR_IN_OUT")
            ):
                in_var_block = True
                continue

            # Check if we're exiting a VAR block
            if in_var_block and stripped == "END_VAR":
                in_var_block = False
                continue

            # Skip lines inside VAR blocks
            if in_var_block:
                continue

            # Keep all other lines
            result_lines.append(line)

        result = "\n".join(result_lines)

        # Strip return types from function signatures for B&R
        # Only match at start of line (after whitespace) to avoid matching function calls
        function_pattern = r"^(\s*FUNCTION\s+\w+)\s*:\s*\w+(\s*\(\*.*?\*\))?"
        result = re.sub(
            function_pattern, r"\1\2", result, flags=re.MULTILINE | re.IGNORECASE
        )

        # Clean up extra blank lines
        result = re.sub(r"\n\s*\n\s*\n", "\n\n", result)

        return result

    def generate_fun_from_template(
        self, template_content: str, tokens: Dict[str, str]
    ) -> str:
        """
        Generate B&R .fun file from complete template by extracting function headers and VAR sections

        Args:
            template_content: Complete template with function implementations
            tokens: Platform-specific token values

        Returns:
            .fun file content with function declarations only
        """
        lines = []
        lines.append(tokens.get("PLATFORM_HEADER", ""))
        lines.append("(* nanoPB function declarations for B&R Automation Studio *)")
        lines.append("")

        # Find all function blocks
        function_blocks = self._find_function_blocks(template_content)

        for block in function_blocks:
            # Extract just the header and VAR sections, skip implementation
            fun_declaration = self._extract_function_declaration_only(block, tokens)
            if fun_declaration:
                lines.append(fun_declaration)
                lines.append("")

        return "\n".join(lines)

    def _extract_function_declaration_only(
        self, block: str, tokens: Dict[str, str]
    ) -> str:
        """Extract function header and VAR sections only, skip implementation"""
        lines = []
        var_depth = 0
        found_function_header = False

        for line in block.split("\n"):
            line_stripped = line.strip().upper()

            # Skip empty lines before function start
            if not lines and not line.strip():
                continue

            # Track function header
            if line_stripped.startswith("FUNCTION"):
                lines.append(self._substitute_tokens(line, tokens))
                found_function_header = True
                continue

            # If we haven't found function header yet, skip
            if not found_function_header:
                continue

            # Track VAR section depth
            if line_stripped.startswith("VAR"):
                var_depth += 1
                lines.append(self._substitute_tokens(line, tokens))
                continue

            if line_stripped.startswith("END_VAR"):
                lines.append(self._substitute_tokens(line, tokens))
                var_depth -= 1
                continue

            # If we're in a VAR section, include the line
            if var_depth > 0:
                lines.append(self._substitute_tokens(line, tokens))
                continue

            # After all VAR sections are done, end the function
            if var_depth == 0 and found_function_header:
                # Only add END_FUNCTION if we haven't already
                if not lines or not lines[-1].strip().upper().startswith("END_VAR"):
                    lines.append("END_FUNCTION")
                    break

            # Skip implementation code and other content

        # Ensure we end with END_FUNCTION
        if lines and not lines[-1].strip().upper() == "END_FUNCTION":
            lines.append("END_FUNCTION")

        return "\n".join(lines)

    def _find_function_blocks(self, content: str) -> List[str]:
        """Find all FUNCTION...END_FUNCTION blocks that are not commented out"""
        # First, remove all comment blocks to avoid matching functions inside comments
        content_without_comments = self._remove_comment_blocks(content)
        
        pattern = r"(FUNCTION\s+\w+.*?END_FUNCTION)"
        matches = re.findall(pattern, content_without_comments, re.DOTALL | re.IGNORECASE)
        return matches

    def _remove_comment_blocks(self, content: str) -> str:
        """Remove ST-style comment blocks (* ... *) from content"""
        # Handle nested comments by tracking depth
        result = []
        i = 0
        comment_depth = 0
        
        while i < len(content):
            if i < len(content) - 1:
                if content[i:i+2] == '(*':
                    comment_depth += 1
                    i += 2
                    continue
                elif content[i:i+2] == '*)':
                    if comment_depth > 0:
                        comment_depth -= 1
                    i += 2
                    continue
            
            if comment_depth == 0:
                result.append(content[i])
            
            i += 1
        
        return ''.join(result)
        return matches

    def _parse_function_declaration(self, block: str) -> Optional[FunctionDeclaration]:
        """Parse a complete function block to extract declaration info"""
        # Extract function header
        header_match = re.search(self.function_header_pattern, block, re.IGNORECASE)
        if not header_match:
            return None

        name = header_match.group(1)
        return_type = header_match.group(2) or "BOOL"  # Default return type
        description = header_match.group(3).strip() if header_match.group(3) else None

        # Parse category/group from description
        group, category = self._extract_metadata(description)

        # Extract VAR sections
        inputs = self._parse_var_section(block, "VAR_INPUT")
        outputs = self._parse_var_section(block, "VAR_OUTPUT")
        in_out = self._parse_var_section(block, "VAR_IN_OUT")
        locals = self._parse_var_section(block, "VAR")

        return FunctionDeclaration(
            name=name,
            return_type=return_type,
            inputs=inputs,
            outputs=outputs,
            in_out=in_out,
            locals=locals,
            description=description,
            group=group,
            category=category,
        )

    def _parse_var_section(self, block: str, var_type: str) -> List[Parameter]:
        """Parse a specific VAR section"""
        pattern = rf"{var_type}\s*(.*?)\s*END_VAR"
        match = re.search(pattern, block, re.DOTALL | re.IGNORECASE)

        if not match:
            return []

        var_content = match.group(1)
        parameters = []

        # Parse individual variable lines
        for line in var_content.split("\n"):
            line = line.strip()
            if not line or line.startswith("(*") or line.startswith("//"):
                continue

            # Match: name : type ; (* comment *)
            var_match = re.match(
                r"(\w+)\s*:\s*([^;]+)(?:\s*;\s*(?:\(\*([^)]*)\*\))?)?", line
            )
            if var_match:
                param_name = var_match.group(1)
                param_type = var_match.group(2).strip().rstrip(";")
                comment = var_match.group(3).strip() if var_match.group(3) else None

                parameters.append(
                    Parameter(name=param_name, type=param_type, comment=comment)
                )

        return parameters

    def _extract_metadata(
        self, description: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """Extract group and category from description"""
        if not description:
            return None, None

        group_match = re.search(r"\$GROUP=([^,\$)]+)", description)
        cat_match = re.search(r"\$CAT=([^,\$)]+)", description)

        group = group_match.group(1) if group_match else None
        category = cat_match.group(1) if cat_match else None

        return group, category

    def _generate_single_fun_declaration(
        self, func: FunctionDeclaration, tokens: Dict[str, str]
    ) -> str:
        """Generate single function declaration for .fun file"""
        lines = []

        # Function header
        desc = func.description or f"Function {func.name}"
        lines.append(f"FUNCTION {func.name} : {func.return_type} (*{desc}*)")

        # VAR_INPUT section
        if func.inputs:
            lines.append("\tVAR_INPUT")
            for param in func.inputs:
                param_type = self._substitute_tokens(param.type, tokens)
                comment = f" (* {param.comment} *)" if param.comment else ""
                lines.append(f"\t\t{param.name} : {param_type};{comment}")
            lines.append("\tEND_VAR")

        # VAR_OUTPUT section
        if func.outputs:
            lines.append("\tVAR_OUTPUT")
            for param in func.outputs:
                param_type = self._substitute_tokens(param.type, tokens)
                comment = f" (* {param.comment} *)" if param.comment else ""
                lines.append(f"\t\t{param.name} : {param_type};{comment}")
            lines.append("\tEND_VAR")

        # VAR_IN_OUT section
        if func.in_out:
            lines.append("\tVAR_IN_OUT")
            for param in func.in_out:
                param_type = self._substitute_tokens(param.type, tokens)
                comment = f" (* {param.comment} *)" if param.comment else ""
                lines.append(f"\t\t{param.name} : {param_type};{comment}")
            lines.append("\tEND_VAR")

        # VAR section (locals only - don't duplicate inputs)
        if func.locals:
            lines.append("\tVAR")
            for param in func.locals:
                param_type = self._substitute_tokens(param.type, tokens)
                comment = f" (* {param.comment} *)" if param.comment else ""
                lines.append(f"\t\t{param.name} : {param_type};{comment}")
            lines.append("\tEND_VAR")

        lines.append("END_FUNCTION")

        return "\n".join(lines)

    def _substitute_tokens(self, type_str: str, tokens: Dict[str, str]) -> str:
        """Substitute platform tokens in type string"""
        result = type_str
        for token, value in tokens.items():
            token_pattern = f"{{{{{token}}}}}"
            if token_pattern in result:
                result = result.replace(token_pattern, value)
        return result


if __name__ == "__main__":
    # Test the processor
    processor = FunctionProcessor()

    # Test with pb_codec template
    try:
        with open("templates/pb_codec.st.template", "r") as f:
            content = f.read()

        functions = processor.extract_function_declarations(content)
        print(f"Found {len(functions)} functions:")
        for name in functions:
            print(f"  - {name}")

        # Test stripping VAR sections
        stripped = processor.strip_var_sections(content)
        print(f"\nStripped content length: {len(stripped)} chars")

    except FileNotFoundError:
        print("Test files not found - run from runtime directory")
