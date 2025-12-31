#!/usr/bin/env python3
"""
Build script to create standalone executables for UEFIReader.

This script uses PyInstaller to compile the Python UEFIReader into
standalone executables for different platforms and architectures.

Usage:
    python build.py --platform linux --arch x64
    python build.py --platform windows --arch x64
    python build.py --all
"""

import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path


def get_pyinstaller_command(platform_name, arch):
    """Generate PyInstaller command for the given platform and architecture."""
    
    # Base command
    cmd = [
        'pyinstaller',
        '--onefile',
        '--name', 'uefireader',
        '--console',
        '--clean',
    ]
    
    # Add platform-specific options
    if platform_name == 'windows':
        cmd.extend([
            '--icon', 'NONE',
        ])
    
    # Add the main script
    cmd.append('uefireader_cli.py')
    
    # Set output directory based on platform and architecture
    output_dir = f'dist/{platform_name}_{arch}'
    cmd.extend(['--distpath', output_dir])
    
    return cmd


def build_executable(platform_name, arch):
    """Build executable for the specified platform and architecture."""
    
    print(f"\n{'='*60}")
    print(f"Building UEFIReader for {platform_name} {arch}")
    print(f"{'='*60}\n")
    
    # Check if PyInstaller is installed
    try:
        subprocess.run(['pyinstaller', '--version'], 
                      capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: PyInstaller is not installed.")
        print("Install it with: pip install pyinstaller")
        return False
    
    # Generate command
    cmd = get_pyinstaller_command(platform_name, arch)
    
    # Run PyInstaller
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n[OK] Successfully built for {platform_name} {arch}")
        
        # Show output location
        output_dir = f'dist/{platform_name}_{arch}'
        exe_name = 'uefireader.exe' if platform_name == 'windows' else 'uefireader'
        exe_path = os.path.join(output_dir, exe_name)
        
        if os.path.exists(exe_path):
            size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print(f"  Output: {exe_path}")
            print(f"  Size: {size:.2f} MB")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n[FAILED] Failed to build for {platform_name} {arch}")
        print(f"  Error: {e}")
        return False


def clean_build_artifacts():
    """Clean up build artifacts."""
    import shutil
    
    artifacts = ['build', 'uefireader.spec']
    for artifact in artifacts:
        if os.path.exists(artifact):
            if os.path.isdir(artifact):
                shutil.rmtree(artifact)
            else:
                os.remove(artifact)
            print(f"Cleaned: {artifact}")


def main():
    parser = argparse.ArgumentParser(
        description='Build UEFIReader standalone executables'
    )
    parser.add_argument(
        '--platform',
        choices=['linux', 'windows', 'darwin'],
        help='Target platform (linux, windows, darwin/macos)'
    )
    parser.add_argument(
        '--arch',
        choices=['x64', 'x86', 'arm64'],
        help='Target architecture (x64, x86, arm64)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Build for current platform with native architecture'
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean build artifacts before building'
    )
    
    args = parser.parse_args()
    
    # Clean if requested
    if args.clean:
        clean_build_artifacts()
    
    # Initialize variables
    platform_name = None
    arch = None
    
    # Determine what to build
    if args.all:
        # Build for current platform
        current_platform = platform.system().lower()
        if current_platform == 'darwin':
            platform_name = 'darwin'
        else:
            platform_name = current_platform
        
        # Determine architecture
        machine = platform.machine().lower()
        if machine in ['x86_64', 'amd64']:
            arch = 'x64'
        elif machine in ['i386', 'i686']:
            arch = 'x86'
        elif machine in ['arm64', 'aarch64']:
            arch = 'arm64'
        else:
            arch = 'x64'  # default
        
        success = build_executable(platform_name, arch)
        
    elif args.platform and args.arch:
        platform_name = args.platform
        arch = args.arch
        success = build_executable(args.platform, args.arch)
        
    else:
        parser.print_help()
        return
    
    # Clean up after build
    clean_build_artifacts()
    
    print(f"\n{'='*60}")
    if success:
        print("Build completed successfully!")
        print("\nTo test the executable:")
        output_dir = f'dist/{args.platform if args.platform else platform_name}_{args.arch if args.arch else arch}'
        exe_name = 'uefireader.exe' if (args.platform == 'windows' or platform_name == 'windows') else 'uefireader'
        print(f"  {os.path.join(output_dir, exe_name)} --help")
    else:
        print("Build failed. Check the error messages above.")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
