# Building and Release Guide

This document explains how to build and release the Client Data Manager application.

## Prerequisites

### Required Tools
- Python 3.8+ (recommended: 3.11)
- [uv](https://astral.sh/uv/) (recommended) or pip
- Git

### Installing uv (Recommended)

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Development Setup

### Quick Start with uv
```bash
# Clone the repository
git clone https://github.com/artchsh/fullstack-dev-crm.git
cd client-data-manager

# Install dependencies
uv sync --dev

# Run the application
uv run python src/main.py

# Run tests
uv run pytest

# Format code
uv run black src tests
uv run isort src tests

# Lint code
uv run flake8 src tests
uv run mypy src
```

### Alternative Setup with pip
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install in development mode
pip install -e .[dev]

# Run the application
python src/main.py
```

## Building Executables

### Using the Build Script
```bash
# Build for current platform
uv run python scripts/build.py
# or
python scripts/build.py

# Executable will be in dist/ directory
```

### Manual PyInstaller Build
```bash
# Install PyInstaller
uv add --dev pyinstaller
# or
pip install pyinstaller

# Build with spec file (recommended)
uv run pyinstaller client-data-manager.spec
# or
pyinstaller client-data-manager.spec

# Build without spec file
uv run pyinstaller --onefile --windowed --name client-data-manager src/main.py
# or
pyinstaller --onefile --windowed --name client-data-manager src/main.py
```

## Release Process

### Automated Releases (Recommended)

The project uses GitHub Actions for automated building and releasing:

1. **On every commit to master:**
   - Runs tests across multiple Python versions
   - Builds executables for Windows, macOS, and Linux
   - Creates a pre-release with downloadable binaries

2. **For official releases:**
   - Create a GitHub release
   - Builds and attaches executables for all platforms

### Manual Version Bump and Release

```bash
# Bump version (patch, minor, or major)
uv run python scripts/bump_version.py patch
# or
python scripts/bump_version.py patch

# Push changes and tags
git push origin master --tags
```

## CI/CD Workflows

### Workflow Files

- `.github/workflows/ci.yml`: Continuous integration (tests, linting)
- `.github/workflows/build-and-release.yml`: Build and release automation

## Package Management Compatibility

The project supports both **uv** (recommended) and **pip**:

### uv Benefits
- ⚡ **Faster**: 10-100x faster than pip
- 🔒 **Reliable**: Built-in dependency resolution
- 🎯 **Modern**: Built in Rust, designed for Python
- 🔄 **Compatible**: Works with existing pip/PyPI ecosystem

### Fallback Support
All scripts and workflows include pip fallbacks:
- If uv is not available, automatically falls back to pip
- Maintains compatibility with existing Python environments
- Works in all CI/CD environments
