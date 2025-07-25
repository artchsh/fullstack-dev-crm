# UV Package Manager Usage

This project uses [UV](https://docs.astral.sh/uv/) as the Python package manager for fast and reliable dependency management.

## Setup

1. **Install UV** (if not already installed):
   ```bash
   # On Windows (PowerShell)
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # On macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Create and activate virtual environment**:
   ```bash
   # UV automatically manages virtual environments
   # No need to manually create/activate venv
   ```

## Development Workflow

### Install Dependencies

```bash
# Install project in development mode with all dev dependencies
uv pip install -e .[dev]

# Alternative: sync from lock file (if available)
uv sync --dev
```

### Run Tests

```bash
# Run all tests with coverage
uv run pytest

# Run specific test file
uv run pytest tests/test_basic.py

# Run tests with verbose output
uv run pytest -v

# Run tests with coverage report
uv run pytest --cov=src --cov-report=term-missing
```

### Code Quality Tools

```bash
# Format code with black
uv run black src/

# Check code formatting
uv run black --check src/

# Lint with flake8
uv run flake8 src/

# Type checking with mypy
uv run mypy src/

# Sort imports with isort
uv run isort src/

# Run pre-commit hooks
uv run pre-commit run --all-files
```

### Build Application

```bash
# Build executable with PyInstaller
uv run pyinstaller --onefile --windowed --name client-data-manager src/main.py
```

## Project Structure

```
client-data-manager/
├── pyproject.toml          # Project configuration and dependencies
├── uv.lock                 # Lock file with exact dependency versions
├── src/                    # Source code
├── tests/                  # Test files
└── .venv/                  # Virtual environment (auto-created by UV)
```

## Dependencies

### Runtime Dependencies
- `cryptography>=45.0.5` - Encryption/decryption functionality
- `flask>=3.1.1` - Web server framework  
- `flask-cors>=6.0.1` - CORS support for Flask
- `sqlalchemy>=2.0.41` - Database ORM
- `ttkbootstrap>=1.14.1` - Modern Tkinter themes

### Development Dependencies
- `pytest>=7.0.0` - Testing framework
- `pytest-cov>=4.0.0` - Coverage reporting
- `black>=23.0.0` - Code formatting
- `flake8>=6.0.0` - Code linting
- `mypy>=1.0.0` - Type checking
- `isort>=5.0.0` - Import sorting
- `pre-commit>=3.0.0` - Git hooks
- `pyinstaller>=5.0.0` - Executable building
- `build>=0.10.0` - Package building
- `twine>=4.0.0` - Package publishing

## Why UV?

- **Fast**: 10-100x faster than pip
- **Reliable**: Deterministic dependency resolution
- **Drop-in replacement**: Compatible with pip/pip-tools workflows
- **Modern**: Built-in virtual environment management
- **Secure**: Lock file ensures reproducible builds

## Troubleshooting

### Common Issues

1. **Pytest not found**:
   ```bash
   # Ensure dev dependencies are installed
   uv pip install -e .[dev]
   ```

2. **Import errors in tests**:
   ```bash
   # Make sure project is installed in development mode
   uv pip install -e .
   ```

3. **Virtual environment issues**:
   ```bash
   # UV manages venv automatically, but you can reset if needed
   rm -rf .venv
   uv pip install -e .[dev]
   ```

### Checking Installation

```bash
# Verify UV is working
uv --version

# List installed packages
uv pip list

# Check if dev dependencies are installed
uv pip list | grep pytest
```

## CI/CD Integration

The project's GitHub Actions workflows use UV for:
- Dependency installation: `uv pip install -e .[dev]`
- Test execution: `uv run pytest`
- Code quality checks: `uv run black`, `uv run flake8`, etc.
- Building executables: `uv run pyinstaller`

This ensures fast and reliable CI/CD pipelines with consistent dependency resolution across all environments.
