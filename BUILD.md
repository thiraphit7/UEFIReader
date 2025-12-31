# Building Standalone Executables

This document describes how to build standalone executables of UEFIReader for different platforms and architectures.

## Overview

UEFIReader can be compiled into standalone executables for:
- **Linux**: x64, x86, arm64
- **Windows**: x64, x86, arm64

The executables include the Python interpreter and all dependencies, so they can run on systems without Python installed.

## Prerequisites

### Python and PyInstaller

You need Python 3.6+ and PyInstaller:

```bash
pip install pyinstaller
```

## Building Executables

### Option 1: Automated Build Scripts

#### Linux

```bash
chmod +x build_linux.sh
./build_linux.sh
```

This will build a standalone executable for your current Linux architecture.

#### Windows

```cmd
build_windows.bat
```

This will build a standalone executable for your current Windows architecture.

### Option 2: Manual Build with Python Script

Build for current platform:
```bash
python build.py --all
```

Build for specific platform and architecture:
```bash
# Linux x64
python build.py --platform linux --arch x64

# Windows x64
python build.py --platform windows --arch x64

# Linux ARM64
python build.py --platform linux --arch arm64

# Windows x86 (32-bit)
python build.py --platform windows --arch x86
```

Clean build artifacts:
```bash
python build.py --clean --all
```

### Option 3: Direct PyInstaller Command

```bash
# Basic build
pyinstaller --onefile --name uefireader python_uefi_reader/__main__.py

# With custom output directory
pyinstaller --onefile --name uefireader --distpath dist/linux_x64 python_uefi_reader/__main__.py
```

## Output

After building, executables will be in:
```
dist/
├── linux_x64/
│   └── uefireader
├── linux_arm64/
│   └── uefireader
├── windows_x64/
│   └── uefireader.exe
└── windows_x86/
    └── uefireader.exe
```

## Testing the Executable

### Linux
```bash
./dist/linux_x64/uefireader --help
./dist/linux_x64/uefireader <input_uefi_image> <output_directory>
```

### Windows
```cmd
dist\windows_x64\uefireader.exe --help
dist\windows_x64\uefireader.exe <input_uefi_image> <output_directory>
```

## Usage

The standalone executable has the same interface as the Python version:

```bash
uefireader <Path to UEFI image/XBL image> <Output Directory>
```

### Examples

```bash
# Linux
./uefireader firmware.bin output/

# Windows
uefireader.exe firmware.bin output\
```

## Cross-Platform Building

**Note**: PyInstaller builds executables for the platform it runs on. To build for:
- **Linux executables**: Run the build on a Linux machine
- **Windows executables**: Run the build on a Windows machine
- **ARM64 executables**: Run the build on an ARM64 machine

For cross-compilation, you would need to:
1. Use a CI/CD system with multiple platform runners
2. Use Docker containers for Linux builds
3. Use virtual machines or cloud instances

## Build Artifacts

The build process creates:
- `build/` - Temporary build files (automatically cleaned)
- `dist/` - Final executables
- `uefireader.spec` - PyInstaller specification file (automatically cleaned)

## Troubleshooting

### PyInstaller Not Found
```bash
pip install pyinstaller
```

### Missing Dependencies
If the executable fails to run, ensure all dependencies are included:
```bash
pyinstaller --onefile --hidden-import=lzma --hidden-import=gzip python_uefi_reader/__main__.py
```

### Large Executable Size
The executable includes the Python interpreter and standard library. Typical sizes:
- Linux: 8-15 MB
- Windows: 10-18 MB

To reduce size, use:
```bash
pyinstaller --onefile --strip python_uefi_reader/__main__.py
```

### Permission Denied (Linux)
```bash
chmod +x dist/linux_x64/uefireader
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build Executables

on: [push]

jobs:
  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install pyinstaller
      - run: python build.py --platform linux --arch x64
      - uses: actions/upload-artifact@v3
        with:
          name: uefireader-linux-x64
          path: dist/linux_x64/uefireader

  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install pyinstaller
      - run: python build.py --platform windows --arch x64
      - uses: actions/upload-artifact@v3
        with:
          name: uefireader-windows-x64
          path: dist/windows_x64/uefireader.exe
```

## Distribution

After building, you can distribute the executables:

1. Create a release on GitHub
2. Upload the executables as release assets
3. Users can download and run without installing Python

## Security Note

Standalone executables include the full Python interpreter and standard library. Ensure you:
- Build from trusted source code
- Scan executables with antivirus software
- Verify checksums before distribution
- Sign executables (recommended for Windows)

## License

The standalone executables are subject to the same MIT license as the source code.
