"""
UEFIReader - Python implementation

Tool to generate .inf payloads for use in various other UEFI projects
out of an existing UEFI volume.
"""

from .uefi import UEFI, EFI, EFISection

__version__ = '1.0.0'
__all__ = ['UEFI', 'EFI', 'EFISection']
