#!/usr/bin/env python3
"""
UEFIReader - Tool to generate .inf payloads for use in various other UEFI projects
out of an existing UEFI volume.

Python port from the original C# implementation.
"""

import sys
import os
from .uefi import UEFI


def extract_qualcomm_uefi_image(uefi_path: str, output: str):
    """Extract Qualcomm UEFI image."""
    with open(uefi_path, 'rb') as f:
        uefi_data = f.read()
    
    uefi = UEFI(uefi_data)
    
    if uefi.build_id:
        output = os.path.join(output, uefi.build_id)
    
    uefi.extract_uefi(output)


def main():
    """Main entry point."""
    if len(sys.argv) == 3 and os.path.exists(sys.argv[1]):
        extract_qualcomm_uefi_image(sys.argv[1], sys.argv[2])
    else:
        print("Usage: <Path to UEFI image/XBL image> <Output Directory>")
        sys.exit(1)


if __name__ == '__main__':
    main()
