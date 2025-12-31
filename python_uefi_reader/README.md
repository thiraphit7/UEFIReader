# UEFIReader - Python Implementation

Python port of UEFIReader - a tool to generate .inf payloads for use in various other UEFI projects out of an existing UEFI volume.

## Overview

This is a Python implementation of the original C# UEFIReader tool. It provides the same functionality for parsing and extracting UEFI firmware images, particularly Qualcomm UEFI/XBL images.

## Features

- Parse UEFI firmware volumes
- Extract DXE drivers and modules
- Generate .inf files for UEFI components
- Support for LZMA and GZip compressed sections
- Extract raw files and APRIORI load lists

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only Python standard library)

## Installation

No installation required. The tool can be run directly from the source directory.

## Usage

```bash
python -m python_uefi_reader <Path to UEFI image/XBL image> <Output Directory>
```

Or run directly:

```bash
python python_uefi_reader/__main__.py <Path to UEFI image/XBL image> <Output Directory>
```

### Example

```bash
python -m python_uefi_reader /path/to/uefi.img /path/to/output
```

## Output

The tool will extract:
- DXE drivers with .inf files
- PE32 executables (.efi files)
- DEPEX files (.depex files)
- Raw files
- DXE.inc - Load list for DXE drivers
- DXE.dsc.inc - Include list for DSC files
- APRIORI.inc - APRIORI load list

## File Structure

```
python_uefi_reader/
├── __init__.py          # Package initialization
├── __main__.py          # Main entry point
├── byte_operations.py   # Byte manipulation utilities
├── converter.py         # Hex string conversion utilities
├── gzip_helper.py       # GZip compression/decompression
├── lzma_helper.py       # LZMA compression/decompression
├── uefi.py             # Main UEFI parsing logic
├── requirements.txt     # Python dependencies (empty - no external deps)
└── README.md           # This file
```

## Differences from C# Version

This Python implementation:
- Uses Python's built-in `gzip` and `lzma` modules instead of external libraries
- Does not include the full 7zip SDK (uses Python's lzma module)
- Has the same core functionality as the C# version
- Uses Python conventions (snake_case instead of PascalCase)

## License

Copyright (c) 2018, Rene Lergner - @Heathcliff74xda

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

## Credits

- Original C# implementation by Rene Lergner (@Heathcliff74xda)
- Python port: 2025

## See Also

- [Original C# UEFIReader](../UEFIReader/)
