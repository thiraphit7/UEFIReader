# UEFIReader
Tool to generate .inf payloads for use in various other UEFI projects out of an existing UEFI volume

## Available Implementations

This repository contains two implementations of UEFIReader:

1. **C# Implementation** (Original) - Located in `UEFIReader/` directory
   - Requires .NET 8.0 or higher
   - Includes full 7zip SDK for LZMA compression

2. **Python Implementation** - Located in `python_uefi_reader/` directory
   - Requires Python 3.6 or higher
   - No external dependencies (uses Python standard library)
   - **Standalone executables available** (no Python installation required)
   - See [Python README](python_uefi_reader/README.md) for details

## Usage

### C# Version
```bash
dotnet run --project UEFIReader/UEFIReader.csproj <UEFI image path> <Output directory>
```

### Python Version (from source)
```bash
python -m python_uefi_reader <UEFI image path> <Output directory>
```

### Standalone Executable (no Python required)
```bash
# Linux
./uefireader <UEFI image path> <Output directory>

# Windows
uefireader.exe <UEFI image path> <Output directory>
```

See [BUILD.md](BUILD.md) for instructions on building standalone executables.

## Building Standalone Executables

The Python version can be compiled into standalone executables for:
- **Linux**: x64, x86, arm64
- **Windows**: x64, x86, arm64

### Quick Build

Linux:
```bash
chmod +x build_linux.sh
./build_linux.sh
```

Windows:
```cmd
build_windows.bat
```

See [BUILD.md](BUILD.md) for detailed build instructions.

## License

MIT License - See LICENSE file for details
