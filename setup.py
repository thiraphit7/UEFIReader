#!/usr/bin/env python3
"""
Setup script for UEFIReader Python implementation.
"""

import os
from setuptools import setup, find_packages

# Read README from the correct location
readme_path = os.path.join(os.path.dirname(__file__), 'python_uefi_reader', 'README.md')
try:
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = 'Tool to generate .inf payloads for UEFI projects from UEFI volumes'

setup(
    name='uefi-reader',
    version='1.0.0',
    description='Tool to generate .inf payloads for UEFI projects from UEFI volumes',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Rene Lergner',
    author_email='',
    url='https://github.com/thiraphit7/UEFIReader',
    packages=find_packages(),
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Embedded Systems',
    ],
    entry_points={
        'console_scripts': [
            'uefi-reader=python_uefi_reader.__main__:main',
        ],
    },
)
