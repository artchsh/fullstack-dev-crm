#!/usr/bin/env python3
"""
Script to bump version and create a new release.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


def get_current_version():
    """Get the current version from src/__init__.py"""
    init_file = Path("src/__init__.py")
    if not init_file.exists():
        raise FileNotFoundError("src/__init__.py not found")
    
    content = init_file.read_text()
    match = re.search(r'__version__ = ["\']([^"\']+)["\']', content)
    if not match:
        raise ValueError("Version not found in src/__init__.py")
    
    return match.group(1)


def update_version(new_version):
    """Update version in src/__init__.py"""
    init_file = Path("src/__init__.py")
    content = init_file.read_text()
    
    # Update version
    content = re.sub(
        r'__version__ = ["\'][^"\']+["\']',
        f'__version__ = "{new_version}"',
        content
    )
    
    init_file.write_text(content)
    print(f"Updated version to {new_version} in src/__init__.py")


def run_command(cmd, check=True):
    """Run a command and return the result"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error running command: {cmd}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)
    return result


def bump_version(version_type):
    """Bump version based on type (major, minor, patch)"""
    current = get_current_version()
    major, minor, patch = map(int, current.split('.'))
    
    if version_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif version_type == 'minor':
        minor += 1
        patch = 0
    elif version_type == 'patch':
        patch += 1
    else:
        raise ValueError("version_type must be 'major', 'minor', or 'patch'")
    
    return f"{major}.{minor}.{patch}"


def main():
    parser = argparse.ArgumentParser(description="Bump version and create release")
    parser.add_argument(
        "version_type",
        choices=["major", "minor", "patch"],
        help="Type of version bump"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually doing it"
    )
    
    args = parser.parse_args()
    
    # Get current and new version
    current_version = get_current_version()
    new_version = bump_version(args.version_type)
    
    print(f"Current version: {current_version}")
    print(f"New version: {new_version}")
    
    if args.dry_run:
        print("Dry run - no changes made")
        return
    
    # Update version
    update_version(new_version)
    
    # Git operations
    run_command("git add src/__init__.py")
    run_command(f'git commit -m "Bump version to {new_version}"')
    run_command(f"git tag v{new_version}")
    
    print(f"Version bumped to {new_version} and tagged")
    print("Run 'git push origin master --tags' to push changes and trigger release")


if __name__ == "__main__":
    main()
