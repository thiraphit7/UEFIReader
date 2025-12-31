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

import os
import re
import sys
import uuid
from datetime import datetime
from typing import List, Tuple, Optional
from . import byte_operations
from . import gzip_helper
from . import lzma_helper


class EFISection:
    """Represents an EFI section."""
    def __init__(self):
        self.name: Optional[str] = None
        self.type: Optional[str] = None
        self.decompressed_image: Optional[bytes] = None


class EFI:
    """Represents an EFI file."""
    def __init__(self):
        self.guid: Optional[uuid.UUID] = None
        self.type: Optional[str] = None
        self.section_elements: List[EFISection] = []


class UEFI:
    """Main UEFI parser class."""
    
    def __init__(self, uefi_binary: bytes, verbose: bool = True):
        self.efis: List[EFI] = []
        self.load_priority: set = set()
        self.build_id: str = ""
        self.verbose = verbose
    
    def _log(self, message: str):
        """Log debug message if verbose mode is enabled."""
        if self.verbose:
            print(message, file=sys.stderr)
        
        # Find UEFI volume header
        offset = byte_operations.find_ascii(uefi_binary, "_FVH")
        if offset is None:
            raise ValueError("Invalid UEFI image format")
        
        volume_header_offset = offset - 0x28
        
        # Parse the volume
        self.efis.extend(self._handle_volume_image(uefi_binary, volume_header_offset))
        
        # Try to get build ID
        build_ids = self._try_get_build_path(uefi_binary)
        if len(build_ids) > 0:
            self.build_id = build_ids[0]
    
    def extract_uefi(self, output: str):
        """Extract UEFI to output directory."""
        self._extract_dxes(output)
        self._extract_apriori(output)
    
    def _try_get_file_path(self, data: bytes) -> List[str]:
        """Extract file paths from data."""
        pattern = re.compile(rb'[a-zA-Z/\\0-9_\-\.]*\.dll\b')
        results = pattern.findall(data)
        decoded = [r.decode('ascii', errors='ignore') for r in results]
        normalized = [self._normalize_build_path(s) for s in decoded]
        return [s for s in normalized if s.count('/') > 1]
    
    def _try_get_build_path(self, data: bytes) -> List[str]:
        """Extract build path from data."""
        pattern = re.compile(rb'QC_IMAGE_VERSION_STRING=[a-zA-Z/\\0-9_\-\.]*\b')
        results = pattern.findall(data)
        decoded = [r.decode('ascii', errors='ignore') for r in results]
        return [s.replace('QC_IMAGE_VERSION_STRING=', '') for s in decoded]
    
    def _normalize_build_path(self, path: str) -> str:
        """Normalize build path."""
        if 'ARM' in path:
            parts = path.replace('\\', '/').split('/ARM/')
            return parts[-1] if len(parts) > 1 else path
        elif 'AARCH64' in path:
            parts = path.replace('\\', '/').split('/AARCH64/')
            return parts[-1] if len(parts) > 1 else path
        else:
            return path.replace('\\', '/')
    
    def _is_section_with_path(self, section: EFISection) -> bool:
        """Check if section contains path information."""
        return section.type not in ['UI', 'DXE_DEPEX', 'RAW', 'PEI_DEPEX']
    
    def _is_section_with_ui(self, section: EFISection) -> bool:
        """Check if section is a UI section."""
        return section.type == 'UI'
    
    def _extract_dxes(self, output: str):
        """Extract DXE drivers."""
        dxe_load_list = []
        dxe_include_list = []
        
        for element in self.efis:
            sections_with_paths = [s for s in element.section_elements if self._is_section_with_path(s)]
            
            if sections_with_paths:
                file_paths_for_element = []
                for section in sections_with_paths:
                    file_paths_for_element.extend(self._try_get_file_path(section.decompressed_image))
                
                output_path = ""
                module_name = ""
                base_name = ""
                
                uis = [s for s in element.section_elements if self._is_section_with_ui(s)]
                
                if file_paths_for_element:
                    parts = file_paths_for_element[0].split('/')
                    if len(parts) >= 3:
                        output_path = '/'.join(parts[:-3]).replace('/', os.sep)
                        module_name = parts[-3]
                    
                    if len(uis) > 1:
                        raise ValueError("Multiple UI sections found")
                    base_name = uis[0].name if len(uis) == 1 else module_name
                else:
                    if len(uis) > 1:
                        raise ValueError("Multiple UI sections found")
                    elif len(uis) == 1:
                        base_name = uis[0].name
                        module_name = base_name.replace(' ', '_')
                        output_path = base_name.replace(' ', '_')
                
                combined_path = os.path.join(output, output_path)
                if not os.path.exists(combined_path):
                    os.makedirs(combined_path)
                
                module_type = element.type.upper()
                if element.type == 'APPLICATION':
                    module_type = 'UEFI_APPLICATION'
                elif element.type == 'DRIVER':
                    module_type = 'DXE_DRIVER'
                elif element.type == 'SECURITY_CORE':
                    module_type = 'SEC'
                
                has_depex = any(s.type == 'DXE_DEPEX' for s in element.section_elements)
                
                # Generate INF file
                inf_output = (
                    "# ****************************************************************************\n"
                    "# AUTOGENERATED BY UEFIReader\n"
                    f"# AUTOGENED AS {module_name}.inf\n"
                    "# DO NOT MODIFY\n"
                    f"# GENERATED ON: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}Z\n"
                    "\n"
                    "[Defines]\n"
                    "  INF_VERSION    = 0x0001001B\n"
                    f"  BASE_NAME      = {base_name}\n"
                    f"  FILE_GUID      = {str(element.guid).upper()}\n"
                    f"  MODULE_TYPE    = {module_type}\n"
                    "  VERSION_STRING = 1.0\n"
                )
                
                if has_depex:
                    inf_output += "  ENTRY_POINT    = EfiEntry\n"
                
                inf_output += "\n[Binaries.AARCH64]"
                
                for item in element.section_elements:
                    if item.type == 'UI':
                        continue
                    
                    section_type = item.type
                    extension = section_type.lower()
                    
                    if section_type == 'PE32':
                        extension = 'efi'
                    elif section_type == 'DXE_DEPEX':
                        extension = 'depex'
                    
                    output_file_name = f"{module_name}.{extension}"
                    inf_output += f"\n   {section_type}|{output_file_name}|*"
                    
                    file_path = os.path.join(combined_path, output_file_name)
                    if os.path.exists(file_path):
                        raise Exception("File Conflict Detected")
                    
                    with open(file_path, 'wb') as f:
                        f.write(item.decompressed_image)
                
                inf_output += "\n\n"
                if has_depex:
                    inf_output += "[Depex]\n  TRUE\n"
                
                inf_output += (
                    "# AUTOGEN ENDS\n"
                    "# ****************************************************************************\n"
                )
                
                inf_path = os.path.join(combined_path, f"{module_name}.inf")
                with open(inf_path, 'w') as f:
                    f.write(inf_output)
                
                rel_path = os.path.join(output_path, f"{module_name}.inf").replace('\\', '/')
                dxe_load_list.append(f"INF {rel_path}")
                dxe_include_list.append(rel_path)
            
            elif any(self._is_section_with_ui(s) for s in element.section_elements):
                uis = [s for s in element.section_elements if self._is_section_with_ui(s)]
                
                if len(uis) > 1:
                    raise ValueError("Multiple UI sections found")
                
                file_name = uis[0].name
                dxe_load_list.append("")
                dxe_load_list.append(f"FILE FREEFORM = {str(element.guid).upper()} {{")
                
                for section in element.section_elements:
                    el = section.name if section.name else file_name
                    
                    if section.type == 'RAW':
                        combined_path = os.path.join(output, 'RawFiles')
                        real_file_name = file_name.replace(' ', '_').replace('\\', os.sep).replace('/', os.sep)
                        file_dst = os.path.join(combined_path, real_file_name)
                        
                        dir_path = os.path.dirname(file_dst)
                        if not os.path.exists(dir_path):
                            os.makedirs(dir_path)
                        
                        with open(file_dst, 'wb') as f:
                            f.write(section.decompressed_image)
                        
                        dxe_load_list.append(f"    SECTION {section.type} = RawFiles/{file_name.replace(' ', '_').replace(os.sep, '/')}")
                    elif section.type == 'UI':
                        dxe_load_list.append(f'    SECTION {section.type} = "{el}"')
                
                dxe_load_list.append("}")
                dxe_load_list.append("")
            else:
                file_name = str(element.guid)
                
                for section in element.section_elements:
                    if section.type == 'RAW':
                        combined_path = os.path.join(output, 'RawFiles')
                        real_file_name = file_name.replace(' ', '_').replace('\\', os.sep).replace('/', os.sep)
                        file_dst = os.path.join(combined_path, real_file_name)
                        
                        dir_path = os.path.dirname(file_dst)
                        if not os.path.exists(dir_path):
                            os.makedirs(dir_path)
                        
                        with open(file_dst, 'wb') as f:
                            f.write(section.decompressed_image)
        
        # Write output files
        with open(os.path.join(output, 'DXE.dsc.inc'), 'w') as f:
            f.write('\n'.join(dxe_include_list))
        
        with open(os.path.join(output, 'DXE.inc'), 'w') as f:
            f.write('\n'.join(dxe_load_list))
    
    def _extract_apriori(self, output: str):
        """Extract APRIORI load list."""
        apriori_load_list = ["APRIORI DXE {"]
        
        for element in self.efis:
            sections_with_paths = [s for s in element.section_elements if self._is_section_with_path(s)]
            
            if sections_with_paths:
                file_paths_for_element = []
                for section in sections_with_paths:
                    file_paths_for_element.extend(self._try_get_file_path(section.decompressed_image))
                
                output_path = ""
                module_name = ""
                
                uis = [s for s in element.section_elements if self._is_section_with_ui(s)]
                
                if file_paths_for_element:
                    parts = file_paths_for_element[0].split('/')
                    if len(parts) >= 3:
                        output_path = '/'.join(parts[:-3]).replace('/', os.sep)
                        module_name = parts[-3]
                else:
                    if len(uis) == 1:
                        base_name = uis[0].name
                        module_name = base_name.replace(' ', '_')
                        output_path = base_name.replace(' ', '_')
                
                if element.guid in self.load_priority:
                    rel_path = os.path.join(output_path, f"{module_name}.inf").replace('\\', '/')
                    apriori_load_list.append(f"    INF {rel_path}")
        
        apriori_load_list.append("}")
        
        with open(os.path.join(output, 'APRIORI.inc'), 'w') as f:
            f.write('\n'.join(apriori_load_list))
    
    def _handle_volume_image(self, data: bytes, offset: int) -> List[EFI]:
        """Parse UEFI volume image."""
        volume_header_magic = byte_operations.read_ascii_string(data, offset + 0x28, 4)
        if volume_header_magic != '_FVH':
            raise ValueError("Invalid volume header")
        
        if not self._verify_volume_checksum(data, offset):
            raise ValueError("Volume checksum verification failed")
        
        volume_size = byte_operations.read_uint32(data, offset + 0x20)
        volume_header_size = byte_operations.read_uint16(data, offset + 0x30)
        
        file_header_offset = offset + volume_header_size
        buffer = data[file_header_offset:file_header_offset + volume_size - volume_header_size]
        
        if file_header_offset + len(buffer) > len(data):
            if self.verbose:
                print(f"Warning: Input buffer is too small by {(file_header_offset + len(buffer)) - len(data):08X} bytes.", file=sys.stderr)
        
        return self._handle_file_loop(buffer, 0, file_header_offset)
    
    def _handle_file_loop(self, data: bytes, offset: int, base: int) -> List[EFI]:
        """Parse files in UEFI volume."""
        file_elements = []
        
        if not self._verify_file_checksum(data, offset):
            raise ValueError("File checksum verification failed")
        
        while offset < len(data):
            if offset + 0x18 > len(data):
                return file_elements
            
            file_type, file_size, file_header_size, file_guid = self._read_file_metadata(data, offset)
            
            if offset + file_size > len(data) or file_size == 0:
                return file_elements
            
            # Process different file types
            if file_type == 0x01:  # EFI_FV_FILETYPE_RAW
                self._log("EFI_FV_FILETYPE_RAW")
                buffer = data[offset + file_header_size:offset + file_size]
                efi = EFI()
                efi.type = 'RAW'
                efi.guid = file_guid
                section = EFISection()
                section.name = str(file_guid)
                section.type = 'RAW'
                section.decompressed_image = buffer
                efi.section_elements = [section]
                file_elements.append(efi)
            
            elif file_type == 0x02:  # EFI_FV_FILETYPE_FREEFORM
                if file_guid == uuid.UUID('fc510ee7-ffdc-11d4-bd41-0080c73c8881'):
                    self._log("EFI_FV_FILETYPE_DXE_APRIORI")
                    buffer = data[offset + file_header_size:offset + file_size]
                    elements = self._handle_section_loop(buffer, 0, offset + file_header_size)
                    
                    if len(elements) > 0 and elements[0].type == 'RAW':
                        for i in range(0, len(elements[0].decompressed_image), 16):
                            dependency_guid = byte_operations.read_guid(elements[0].decompressed_image, i)
                            self._log(str(dependency_guid).upper())
                            self.load_priority.add(dependency_guid)
                else:
                    self._log("EFI_FV_FILETYPE_FREEFORM")
                    buffer = data[offset + file_header_size:offset + file_size]
                    elements = self._handle_section_loop(buffer, 0, offset + file_header_size)
                    efi = EFI()
                    efi.type = 'FREEFORM'
                    efi.guid = file_guid
                    efi.section_elements = elements
                    file_elements.append(efi)
            
            elif file_type == 0x03:  # EFI_FV_FILETYPE_SECURITY_CORE
                self._log("EFI_FV_FILETYPE_SECURITY_CORE")
                buffer = data[offset + file_header_size:offset + file_size]
                elements = self._handle_section_loop(buffer, 0, offset + file_header_size)
                efi = EFI()
                efi.type = 'SECURITY_CORE'
                efi.guid = file_guid
                efi.section_elements = elements
                file_elements.append(efi)
            
            elif file_type == 0x05:  # EFI_FV_FILETYPE_DXE_CORE
                self._log("EFI_FV_FILETYPE_DXE_CORE")
                buffer = data[offset + file_header_size:offset + file_size]
                elements = self._handle_section_loop(buffer, 0, offset + file_header_size)
                efi = EFI()
                efi.type = 'DXE_CORE'
                efi.guid = file_guid
                efi.section_elements = elements
                file_elements.append(efi)
            
            elif file_type == 0x07:  # EFI_FV_FILETYPE_DRIVER
                self._log("EFI_FV_FILETYPE_DRIVER")
                buffer = data[offset + file_header_size:offset + file_size]
                elements = self._handle_section_loop(buffer, 0, offset + file_header_size)
                efi = EFI()
                efi.type = 'DRIVER'
                efi.guid = file_guid
                efi.section_elements = elements
                file_elements.append(efi)
            
            elif file_type == 0x09:  # EFI_FV_FILETYPE_APPLICATION
                self._log("EFI_FV_FILETYPE_APPLICATION")
                buffer = data[offset + file_header_size:offset + file_size]
                elements = self._handle_section_loop(buffer, 0, offset + file_header_size)
                efi = EFI()
                efi.type = 'APPLICATION'
                efi.guid = file_guid
                efi.section_elements = elements
                file_elements.append(efi)
            
            elif file_type == 0x0B:  # EFI_FV_FILETYPE_FIRMWARE_VOLUME_IMAGE
                self._log("EFI_FV_FILETYPE_FIRMWARE_VOLUME_IMAGE")
                buffer = data[offset + file_header_size:offset + file_size]
                elements = self._handle_section_loop(buffer, 0, offset + file_header_size)
                for element in elements:
                    if element.type == 'FV':
                        file_elements.extend(self._handle_volume_image(element.decompressed_image, 0))
            
            elif file_type == 0xF0:  # EFI_FV_FILETYPE_FFS_PAD
                self._log("EFI_FV_FILETYPE_FFS_PAD")
            
            elif file_type in [0x00, 0xFF]:
                return file_elements
            
            else:
                self._log(f"Unsupported file type! 0x{file_type:02X} with size 0x{file_size:04X} at offset 0x{offset:04X}")
                raise ValueError("Unsupported file type")
            
            offset += file_size
            offset = byte_operations.align(base, offset, 8)
        
        return file_elements
    
    def _read_section_data_buffer(self, data: bytes, offset: int) -> bytes:
        """Read section data buffer."""
        section_size, _ = self._read_section_metadata(data, offset)
        return data[offset + 4:offset + section_size]
    
    def _handle_section_loop(self, data: bytes, offset: int, base: int) -> List[EFISection]:
        """Parse sections in a file."""
        file_elements = []
        
        while offset < len(data):
            if offset + 4 > len(data):
                raise ValueError("Invalid section data")
            
            section_size, section_type = self._read_section_metadata(data, offset)
            
            if offset + section_size > len(data) or section_size == 0:
                raise ValueError("Invalid section size")
            
            if section_type == 0x02:  # EFI_SECTION_GUID_DEFINED
                self._log("EFI_SECTION_GUID_DEFINED")
                file_elements.extend(self._parse_guid_defined_section(data, offset, base))
            
            elif section_type == 0x10:  # EFI_SECTION_PE32
                self._log("EFI_SECTION_PE32")
                section = EFISection()
                section.type = 'PE32'
                section.decompressed_image = self._read_section_data_buffer(data, offset)
                file_elements.append(section)
            
            elif section_type == 0x11:  # EFI_SECTION_PIC
                self._log("EFI_SECTION_PIC")
                section = EFISection()
                section.type = 'PIC'
                section.decompressed_image = self._read_section_data_buffer(data, offset)
                file_elements.append(section)
            
            elif section_type == 0x12:  # EFI_SECTION_TE
                self._log("EFI_SECTION_TE")
                section = EFISection()
                section.type = 'TE'
                section.decompressed_image = self._read_section_data_buffer(data, offset)
                file_elements.append(section)
            
            elif section_type == 0x13:  # EFI_SECTION_DXE_DEPEX
                self._log("EFI_SECTION_DXE_DEPEX")
                section = EFISection()
                section.type = 'DXE_DEPEX'
                section.decompressed_image = self._read_section_data_buffer(data, offset)
                file_elements.append(section)
            
            elif section_type == 0x14:  # EFI_SECTION_VERSION
                self._log("EFI_SECTION_VERSION")
            
            elif section_type == 0x15:  # EFI_SECTION_USER_INTERFACE
                self._log("EFI_SECTION_USER_INTERFACE")
                section = EFISection()
                section.type = 'UI'
                section.decompressed_image = self._read_section_data_buffer(data, offset)
                section.name = byte_operations.read_unicode_string(data, offset + 4, section_size - 4).rstrip('\x00 ')
                file_elements.append(section)
            
            elif section_type == 0x17:  # EFI_SECTION_FIRMWARE_VOLUME_IMAGE
                self._log("EFI_SECTION_FIRMWARE_VOLUME_IMAGE")
                section = EFISection()
                section.type = 'FV'
                section.decompressed_image = self._read_section_data_buffer(data, offset)
                file_elements.append(section)
            
            elif section_type == 0x18:  # EFI_SECTION_FREEFORM_SUBTYPE_GUID
                self._log("EFI_SECTION_FREEFORM_SUBTYPE_GUID")
                section = EFISection()
                section.type = 'RAW'
                section.decompressed_image = self._read_section_data_buffer(data, offset)
                file_elements.append(section)
            
            elif section_type == 0x19:  # EFI_SECTION_RAW
                self._log("EFI_SECTION_RAW")
                section = EFISection()
                section.type = 'RAW'
                section.decompressed_image = self._read_section_data_buffer(data, offset)
                file_elements.append(section)
            
            elif section_type == 0x1B:  # EFI_SECTION_PEI_DEPEX
                self._log("EFI_SECTION_PEI_DEPEX")
                section = EFISection()
                section.type = 'PEI_DEPEX'
                section.decompressed_image = self._read_section_data_buffer(data, offset)
                file_elements.append(section)
            
            elif section_type in [0x00, 0xFF]:
                return file_elements
            
            else:
                self._log(f"Unsupported section type! 0x{section_type:02X} with size 0x{section_size:04X} at offset 0x{offset:04X}")
                raise ValueError("Unsupported section type")
            
            offset += section_size
            offset = byte_operations.align(base, offset, 4)
        
        return file_elements
    
    def _read_section_metadata(self, data: bytes, offset: int) -> Tuple[int, int]:
        """Read section metadata."""
        section_size = byte_operations.read_uint24(data, offset)
        section_type = byte_operations.read_uint8(data, offset + 3)
        return section_size, section_type
    
    def _read_file_metadata(self, data: bytes, offset: int) -> Tuple[int, int, int, uuid.UUID]:
        """Read file metadata."""
        file_guid = byte_operations.read_guid(data, offset)
        file_type = byte_operations.read_uint8(data, offset + 0x12)
        attributes = byte_operations.read_uint8(data, offset + 0x13)
        file_size = byte_operations.read_uint24(data, offset + 0x14)
        file_header_size = 0x18
        
        if attributes == 0x41:
            file_size = byte_operations.read_uint64(data, offset + 0x18)
            file_header_size = 0x20
        
        return file_type, file_size, file_header_size, file_guid
    
    def _parse_guid_defined_section(self, data: bytes, offset: int, base: int) -> List[EFISection]:
        """Parse GUID-defined section (compressed)."""
        section_size, section_type = self._read_section_metadata(data, offset)
        
        if section_type != 0x02:
            raise ValueError("Not a GUID-defined section")
        
        section_guid = byte_operations.read_guid(data, offset + 4)
        section_header_size = byte_operations.read_uint16(data, offset + 0x14)
        
        compressed_offset = offset + section_header_size
        compressed_size = section_size - section_header_size
        
        # Decompress based on GUID
        lzma_guid1 = uuid.UUID('ee4e5898-3914-4259-9d6e-dc7bd79403cf')
        lzma_guid2 = uuid.UUID('bd9921ea-ed91-404a-8b2f-b4d724747c8c')
        gzip_guid = uuid.UUID('1d301fe9-be79-4353-91c2-d23bc959ae0c')
        
        if section_guid in [lzma_guid1, lzma_guid2]:
            # LZMA decompression
            decompressed_image = lzma_helper.decompress(data, compressed_offset, compressed_size)
        elif section_guid == gzip_guid:
            # GZip decompression
            decompressed_image = gzip_helper.decompress(data, compressed_offset, compressed_size)
        else:
            raise ValueError(f"Unsupported compression GUID: {section_guid}")
        
        return self._handle_section_loop(decompressed_image, 0, base)
    
    def _verify_volume_checksum(self, data: bytes, offset: int) -> bool:
        """Verify volume header checksum."""
        volume_header_size = byte_operations.read_uint16(data, offset + 0x30)
        header = bytearray(data[offset:offset + volume_header_size])
        byte_operations.write_uint16(header, 0x32, 0)  # Clear checksum
        current_checksum = byte_operations.read_uint16(data, offset + 0x32)
        new_checksum = byte_operations.calculate_checksum16(bytes(header), 0, volume_header_size)
        return current_checksum == new_checksum
    
    def _verify_file_checksum(self, data: bytes, offset: int) -> bool:
        """Verify file header checksum."""
        file_header_size = 0x18
        attributes = byte_operations.read_uint8(data, offset + 0x13)
        file_size = byte_operations.read_uint24(data, offset + 0x14)
        
        if attributes == 0x41:
            file_size = byte_operations.read_uint64(data, offset + 0x18)
            file_header_size = 0x20
        
        header = bytearray(data[offset:offset + file_header_size - 1])
        byte_operations.write_uint16(header, 0x10, 0)  # Clear checksum
        current_header_checksum = byte_operations.read_uint8(data, offset + 0x10)
        calculated_header_checksum = byte_operations.calculate_checksum8(bytes(header), 0, file_header_size - 1)
        
        if current_header_checksum != calculated_header_checksum:
            return False
        
        file_attribs = byte_operations.read_uint8(data, offset + 0x13)
        current_file_checksum = byte_operations.read_uint8(data, offset + 0x11)
        
        if (file_attribs & 0x40) > 0:
            # Calculate file checksum
            calculated_file_checksum = byte_operations.calculate_checksum8(data, offset + file_header_size, file_size - file_header_size)
            if current_file_checksum != calculated_file_checksum:
                return False
        else:
            # Fixed file checksum
            if current_file_checksum not in [0xAA, 0x55]:
                return False
        
        return True
