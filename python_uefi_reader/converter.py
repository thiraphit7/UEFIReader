"""
Converter utility functions for hex string operations.
"""


def convert_hex_to_string(bytes_data: bytes, separator: str) -> str:
    """Convert bytes to hex string with separator."""
    return separator.join(f'{b:02X}' for b in bytes_data)


def convert_string_to_hex(hex_string: str) -> bytes:
    """Convert hex string to bytes."""
    if len(hex_string) % 2 == 1:
        raise ValueError("The binary key cannot have an odd number of digits")
    
    return bytes.fromhex(hex_string)


def get_hex_val(hex_char: str) -> int:
    """Get hex value from character."""
    val = ord(hex_char)
    # For uppercase A-F: val - 55
    # For lowercase a-f: val - 87
    # For 0-9: val - 48
    if val < 58:
        return val - 48
    elif val < 97:
        return val - 55
    else:
        return val - 87
