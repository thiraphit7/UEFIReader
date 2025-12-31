#!/usr/bin/env python3
"""
Example usage of the Python UEFIReader implementation.

This script demonstrates how to use the UEFIReader library to parse
and extract UEFI firmware images.
"""

import os
import sys
from python_uefi_reader import UEFI


def example_usage():
    """Example of using the UEFI parser."""
    
    # Check command line arguments
    if len(sys.argv) < 3:
        print("Example Usage:")
        print("  python example.py <UEFI image file> <output directory>")
        print()
        print("Description:")
        print("  This example shows how to parse a UEFI firmware image")
        print("  and extract its components to an output directory.")
        return
    
    uefi_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    # Check if input file exists
    if not os.path.exists(uefi_path):
        print(f"Error: File not found: {uefi_path}")
        return
    
    print(f"Reading UEFI image: {uefi_path}")
    
    # Read the UEFI binary
    with open(uefi_path, 'rb') as f:
        uefi_data = f.read()
    
    print(f"File size: {len(uefi_data)} bytes")
    
    # Parse the UEFI image (with verbose output)
    try:
        print("Parsing UEFI image...")
        uefi = UEFI(uefi_data, verbose=True)
        
        print(f"Found {len(uefi.efis)} EFI files")
        
        if uefi.build_id:
            print(f"Build ID: {uefi.build_id}")
            output_dir = os.path.join(output_dir, uefi.build_id)
        
        # Extract the UEFI components
        print(f"Extracting to: {output_dir}")
        uefi.extract_uefi(output_dir)
        
        print("Extraction complete!")
        print(f"Output files:")
        print(f"  - {os.path.join(output_dir, 'DXE.inc')}")
        print(f"  - {os.path.join(output_dir, 'DXE.dsc.inc')}")
        print(f"  - {os.path.join(output_dir, 'APRIORI.inc')}")
        
    except Exception as e:
        print(f"Error parsing UEFI image: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == '__main__':
    example_usage()
