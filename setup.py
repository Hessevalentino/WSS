#!/usr/bin/env python3
"""
Setup script for WiFi Scanner Suite
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements from requirements.txt if it exists
def read_requirements():
    requirements_file = "requirements.txt"
    if os.path.exists(requirements_file):
        with open(requirements_file, "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    return []

setup(
    name="wifi-scanner-suite",
    version="2.1.2",
    author="OK2HSS",
    author_email="your.email@example.com",  # Replace with actual email
    description="A comprehensive command-line WiFi network scanner with BSSID display, device discovery, and connection utility for Linux systems",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Hessevalentino/WSS",
    py_modules=["wifi_scanner_suite"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "rich": ["rich>=10.0.0"],
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "wss=wifi_scanner_suite:main",
            "wifi-scanner-suite=wifi_scanner_suite:main",
        ],
    },
    keywords="wifi wireless network scanner linux networking security",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/wifi-scanner-suite/issues",
        "Source": "https://github.com/yourusername/wifi-scanner-suite",
        "Documentation": "https://github.com/yourusername/wifi-scanner-suite#readme",
        "Changelog": "https://github.com/yourusername/wifi-scanner-suite/blob/main/CHANGELOG.md",
    },
    include_package_data=True,
    zip_safe=False,
)
