#!/usr/bin/env python3
"""
Standalone entry point for UEFIReader.
This file is designed to work with PyInstaller for creating standalone executables.
"""

import sys
import os

# Add the parent directory to the path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main module directly
from python_uefi_reader.uefi import UEFI


def extract_qualcomm_uefi_image(uefi_path: str, output: str):
    """Extract Qualcomm UEFI image."""
    with open(uefi_path, 'rb') as f:
        uefi_data = f.read()
    
    uefi = UEFI(uefi_data, verbose=True)
    
    if uefi.build_id:
        output = os.path.join(output, uefi.build_id)
    
    uefi.extract_uefi(output)


def main():
    """Main entry point."""
    if len(sys.argv) == 3 and os.path.exists(sys.argv[1]):
        extract_qualcomm_uefi_image(sys.argv[1], sys.argv[2])
    else:
        print("Usage: uefireader <Path to UEFI image/XBL image> <Output Directory>")
        sys.exit(1)


if __name__ == '__main__':
    main()
