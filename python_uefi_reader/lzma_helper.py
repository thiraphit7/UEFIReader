"""
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
"""

import lzma
from . import byte_operations


def decompress(data: bytes, offset: int, input_size: int) -> bytes:
    """Decompress LZMA data."""
    # LZMA format: 5 bytes properties + 8 bytes size + compressed data
    properties = data[offset:offset + 5]
    output_size = byte_operations.read_uint64(data, offset + 5)
    compressed_data = data[offset + 0x0D:offset + input_size]
    
    # Create LZMA decompressor with properties
    filters = [
        {
            "id": lzma.FILTER_LZMA1,
            "preset": None,
            "dict_size": None,
            "lc": properties[0] % 9,
            "lp": (properties[0] // 9) % 5,
            "pb": (properties[0] // 45),
        }
    ]
    
    # Try to decompress using raw format
    try:
        decompressor = lzma.LZMADecompressor(format=lzma.FORMAT_RAW, filters=filters)
        return decompressor.decompress(compressed_data)
    except Exception:
        # Fallback: try with the full data including header
        full_data = data[offset:offset + input_size]
        try:
            return lzma.decompress(full_data)
        except Exception:
            # Last resort: use the properties-based approach
            import struct
            dict_size = struct.unpack('<I', properties[1:5])[0]
            filters = [
                {
                    "id": lzma.FILTER_LZMA1,
                    "dict_size": dict_size,
                    "lc": properties[0] % 9,
                    "lp": (properties[0] // 9) % 5,
                    "pb": (properties[0] // 45),
                }
            ]
            decompressor = lzma.LZMADecompressor(format=lzma.FORMAT_RAW, filters=filters)
            result = decompressor.decompress(compressed_data)
            # Truncate to expected output size if necessary
            return result[:output_size] if len(result) > output_size else result


def compress(data: bytes, offset: int, input_size: int) -> bytes:
    """Compress data using LZMA."""
    input_data = data[offset:offset + input_size]
    return lzma.compress(input_data, format=lzma.FORMAT_ALONE, preset=9)
