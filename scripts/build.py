#!/usr/bin/env python3
"""
Build script for creating executables with PyInstaller.
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path


def run_command(cmd):
    """Run a command and return the result"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0


def install_with_uv():
    """Try to install with uv, fallback to pip"""
    print("Attempting to install with uv...")
    if run_command("uv --version"):
        if run_command("uv sync"):
            if run_command("uv add pyinstaller"):
                return True
    
    print("uv failed, falling back to pip...")
    return False


def install_with_pip():
    """Install with pip"""
    print("Installing with pip...")
    if not run_command("pip install -e ."):
        print("Failed to install package")
        return False
    
    if not run_command("pip install pyinstaller"):
        print("Failed to install PyInstaller")
        return False
    
    return True


def build_executable():
    """Build executable using PyInstaller"""
    
    # Clean previous builds
    dist_dir = Path("dist")
    build_dir = Path("build")
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
        print("Cleaned dist directory")
    
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print("Cleaned build directory")
    
    # Install requirements
    if not install_with_uv():
        if not install_with_pip():
            return False
    
    # Build using spec file if it exists, otherwise use simple command
    spec_file = Path("client-data-manager.spec")
    if spec_file.exists():
        cmd = f"uv run pyinstaller {spec_file}"
        if not run_command(cmd):
            cmd = f"pyinstaller {spec_file}"
            if not run_command(cmd):
                print("Failed to build executable")
                return False
    else:
        cmd = "uv run pyinstaller --onefile --windowed --name client-data-manager src/main.py"
        if not run_command(cmd):
            cmd = "pyinstaller --onefile --windowed --name client-data-manager src/main.py"
            if not run_command(cmd):
                print("Failed to build executable")
                return False
    
    print("Build completed successfully!")
    
    # List created files
    if dist_dir.exists():
        print("\nCreated files:")
        for file in dist_dir.rglob("*"):
            if file.is_file():
                size = file.stat().st_size / (1024 * 1024)  # MB
                print(f"  {file.relative_to(dist_dir)} ({size:.1f} MB)")
    
    return True


def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage: python build.py")
        print("Build executable using PyInstaller")
        return
    
    if not build_executable():
        sys.exit(1)


if __name__ == "__main__":
    main()
