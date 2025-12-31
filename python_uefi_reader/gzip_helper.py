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

import gzip
import io


def decompress(data: bytes, offset: int, input_size: int) -> bytes:
    """Decompress GZip data."""
    compressed_data = data[offset:offset + input_size]
    with gzip.GzipFile(fileobj=io.BytesIO(compressed_data)) as gz:
        return gz.read()


def compress(data: bytes, offset: int, input_size: int) -> bytes:
    """Compress data using GZip."""
    input_data = data[offset:offset + input_size]
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode='wb') as gz:
        gz.write(input_data)
    return output.getvalue()
