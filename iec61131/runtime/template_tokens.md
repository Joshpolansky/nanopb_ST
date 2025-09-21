# nanoPB Runtime Library Template Tokens

This document defines the template token system for generating platform-specific runtime libraries.

## Template Token Format
All template tokens use the format: `{{TOKEN_NAME}}`

## Platform Configuration Tokens

### File Extensions
- `{{FILE_EXT_TYPES}}` - Type definitions (.typ, .DUT)
- `{{FILE_EXT_VARIABLES}}` - Variable declarations (.var, .GVL)  
- `{{FILE_EXT_CODE}}` - Code files (.st, .ST)
- `{{FILE_EXT_FUNCTIONS}}` - Function declarations (.fun, .EXP)
- `{{FILE_EXT_LIBRARY}}` - Library files (.lby, .library)

### Memory Functions
- `{{MEMCPY_FUNC}}` - Memory copy function (brsmemcpy, MEMCPY)
- `{{MEMSET_FUNC}}` - Memory set function (brsmemset, MEMSET)
- `{{STRLEN_FUNC}}` - String length function (brsstrcmp, LEN)

### Pointer and Memory Access
- `{{PTR_ACCESS}}` - Pointer access pattern (ACCESS, ^)
- `{{PTR_DEREF_START}}` - Start of pointer dereference
- `{{PTR_DEREF_END}}` - End of pointer dereference
- `{{ADR_FUNC}}` - Address-of function (ADR)

### Variable Scope Keywords
- `{{SCOPE_CONSTANT}}` - Constant variable scope (VAR_CONSTANT, VAR_GLOBAL CONSTANT)
- `{{SCOPE_GLOBAL}}` - Global variable scope (VAR, VAR_GLOBAL)
- `{{SCOPE_LOCAL}}` - Local variable scope (VAR, VAR)

### Data Types
- `{{TYPE_BYTE}}` - Byte type (USINT, BYTE)
- `{{TYPE_SIZE}}` - Size type (UINT, UINT)
- `{{TYPE_SSIZE}}` - Signed size type (INT, INT)
- `{{TYPE_TYPE}}` - Type field type (USINT, USINT)

### Platform-Specific Headers and Comments
- `{{PLATFORM_HEADER}}` - Platform identification header
- `{{PLATFORM_NAME}}` - Platform name (B&R, Codesys, TwinCAT)
- `{{PLATFORM_INCLUDES}}` - Platform-specific include statements

## Example Usage

### Before (B&R specific):
```st
VAR_CONSTANT
    pb_byte_t : USINT;
END_VAR

FUNCTION example
    src_ptr ACCESS stream.state;
    brsmemcpy(dest, src, size);
END_FUNCTION
```

### After (Template):
```st
{{SCOPE_CONSTANT}}
    {{TYPE_BYTE}} : {{TYPE_BYTE}};
END_VAR

FUNCTION example
    {{PTR_DEREF_START}}src_ptr{{PTR_ACCESS}}stream.state{{PTR_DEREF_END}};
    {{MEMCPY_FUNC}}(dest, src, size);
END_FUNCTION
```

## Platform Token Values

### B&R Automation Studio
```json
{
    "FILE_EXT_TYPES": ".typ",
    "FILE_EXT_VARIABLES": ".var", 
    "FILE_EXT_CODE": ".st",
    "FILE_EXT_FUNCTIONS": ".fun",
    "FILE_EXT_LIBRARY": ".lby",
    "MEMCPY_FUNC": "brsmemcpy",
    "MEMSET_FUNC": "brsmemset", 
    "STRLEN_FUNC": "brsstrcmp",
    "PTR_ACCESS": " ACCESS ",
    "PTR_DEREF_START": "",
    "PTR_DEREF_END": "",
    "ADR_FUNC": "ADR",
    "SCOPE_CONSTANT": "VAR_CONSTANT",
    "SCOPE_GLOBAL": "VAR",
    "SCOPE_LOCAL": "VAR",
    "TYPE_BYTE": "USINT",
    "TYPE_SIZE": "UINT",
    "TYPE_SSIZE": "INT",
    "TYPE_TYPE": "USINT",
    "PLATFORM_NAME": "B&R Automation Studio",
    "PLATFORM_HEADER": "(* nanoPB Runtime Library for B&R Automation Studio *)"
}
```

### Codesys
```json
{
    "FILE_EXT_TYPES": ".DUT",
    "FILE_EXT_VARIABLES": ".GVL",
    "FILE_EXT_CODE": ".ST", 
    "FILE_EXT_FUNCTIONS": ".EXP",
    "FILE_EXT_LIBRARY": ".library",
    "MEMCPY_FUNC": "MEMCPY",
    "MEMSET_FUNC": "MEMSET",
    "STRLEN_FUNC": "LEN", 
    "PTR_ACCESS": "^",
    "PTR_DEREF_START": "",
    "PTR_DEREF_END": "^",
    "ADR_FUNC": "ADR",
    "SCOPE_CONSTANT": "VAR_GLOBAL CONSTANT",
    "SCOPE_GLOBAL": "VAR_GLOBAL",
    "SCOPE_LOCAL": "VAR",
    "TYPE_BYTE": "USINT", 
    "TYPE_SIZE": "UINT",
    "TYPE_SSIZE": "INT",
    "TYPE_TYPE": "USINT",
    "PLATFORM_NAME": "Codesys",
    "PLATFORM_HEADER": "(* nanoPB Runtime Library for Codesys *)"
}
```

### TwinCAT
```json
{
    "FILE_EXT_TYPES": ".DUT",
    "FILE_EXT_VARIABLES": ".GVL", 
    "FILE_EXT_CODE": ".ST",
    "FILE_EXT_FUNCTIONS": ".EXP",
    "FILE_EXT_LIBRARY": ".library",
    "MEMCPY_FUNC": "MEMCPY", 
    "MEMSET_FUNC": "MEMSET",
    "STRLEN_FUNC": "LEN",
    "PTR_ACCESS": "",
    "PTR_DEREF_START": "",
    "PTR_DEREF_END": "",
    "ADR_FUNC": "ADR",
    "SCOPE_CONSTANT": "VAR_GLOBAL CONSTANT",
    "SCOPE_GLOBAL": "VAR_GLOBAL",
    "SCOPE_LOCAL": "VAR", 
    "TYPE_BYTE": "BYTE",
    "TYPE_SIZE": "UINT",
    "TYPE_SSIZE": "INT",
    "TYPE_TYPE": "USINT",
    "PLATFORM_NAME": "TwinCAT",
    "PLATFORM_HEADER": "(* nanoPB Runtime Library for TwinCAT *)"
}
```