#!/bin/bash
#
# Build script for Linux platforms
# Creates standalone executables for x64, x86, and arm64
#

set -e

echo "=================================================="
echo "UEFIReader Linux Build Script"
echo "=================================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Install PyInstaller if not already installed
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "Installing PyInstaller..."
    pip3 install pyinstaller
fi

# Detect current architecture
ARCH=$(uname -m)
case $ARCH in
    x86_64)
        BUILD_ARCH="x64"
        ;;
    i386|i686)
        BUILD_ARCH="x86"
        ;;
    aarch64|arm64)
        BUILD_ARCH="arm64"
        ;;
    *)
        echo "Warning: Unknown architecture $ARCH, defaulting to x64"
        BUILD_ARCH="x64"
        ;;
esac

echo "Building for Linux $BUILD_ARCH..."
echo ""

# Build the executable
python3 build.py --platform linux --arch $BUILD_ARCH

echo ""
echo "=================================================="
echo "Build Complete!"
echo "=================================================="
echo ""
echo "Executable location: dist/linux_${BUILD_ARCH}/uefireader"
echo ""
echo "To test:"
echo "  ./dist/linux_${BUILD_ARCH}/uefireader"
echo ""
