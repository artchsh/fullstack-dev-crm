# LLM Guide for Client Data Manager

This document provides guidance for Large Language Models (LLMs) and AI coding assistants working with the Client Data Manager codebase.

## Project Overview

**Client Data Manager** is a secure desktop application for managing client hosting, database, and website information. It's built with Python, using a modern GUI framework (ttkbootstrap) and secure data storage.

### Key Technologies
- **Frontend**: ttkbootstrap (modern tkinter themes)
- **Backend**: SQLAlchemy ORM with SQLite
- **Security**: Fernet encryption for sensitive data
- **API**: Flask for web services
- **Build**: PyInstaller for executable creation
- **Package Management**: uv (recommended) or pip

## Architecture Overview

```
src/
├── main.py              # Application entry point
├── api/                 # Flask API endpoints
│   └── server.py
├── config/              # Configuration management
│   ├── settings.py      # Application settings
│   └── app_settings.py  # Settings loader
├── database/            # Data layer
│   ├── models.py        # SQLAlchemy models
│   └── db_manager.py    # Database operations
├── gui/                 # User interface
│   ├── main_window.py   # Main application window
│   ├── dialogs.py       # Dialog windows
│   └── settings_dialog.py
└── utils/               # Utilities
    ├── encryption.py    # Data encryption/decryption
    └── clipboard.py     # Clipboard operations
```

## Core Features for LLMs to Understand

### 1. Data Models (database/models.py)

```python
class Client(Base):
    """Main client entity with related hosting, database, and website info"""
    __tablename__ = 'clients'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    hosting = relationship("Hosting", back_populates="client", uselist=False)
    database = relationship("Database", back_populates="client", uselist=False)
    website = relationship("Website", back_populates="client", uselist=False)

class Hosting(Base):
    """Hosting service information"""
    service = Column(String(255))
    service_link = Column(String(500))
    username = Column(String(255))
    password = Column(Text)  # Encrypted
    notes = Column(Text)

class Database(Base):
    """Database connection information"""
    username = Column(String(255))
    database_name = Column(String(255))
    password = Column(Text)  # Encrypted

class Website(Base):
    """Website and domain information"""
    domain = Column(String(255))
    admin_panel_link = Column(String(500))
```

### 2. Encryption (utils/encryption.py)

```python
def encrypt_password(password: str) -> str:
    """Encrypt sensitive data using Fernet symmetric encryption"""
    # Uses PBKDF2 key derivation
    # Returns base64-encoded encrypted string

def decrypt_password(encrypted_password: str) -> str:
    """Decrypt sensitive data"""
    # Handles decryption errors gracefully
    # Returns original password string
```

### 3. GUI Structure (gui/main_window.py)

```python
class MainWindow:
    """Main application window using ttkbootstrap"""
    
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.setup_bindings()
    
    def setup_ui(self):
        # Creates modern UI with:
        # - Client list (Treeview)
        # - Action buttons
        # - Search functionality
        # - Copy to clipboard features
    
    def on_client_select(self, event):
        # Handles client selection
        # Updates UI with client details
    
    def copy_to_clipboard(self, data_type="all"):
        # Formats and copies client data
        # Supports: all, hosting, database, website
```

## Common Development Patterns

### 1. Database Operations

```python
# Creating a new client
def create_client(name: str, email: str = None, phone: str = None):
    with get_session() as session:
        client = Client(name=name, email=email, phone=phone)
        session.add(client)
        session.commit()
        return client

# Adding hosting information
def add_hosting_info(client_id: int, service: str, username: str, password: str):
    with get_session() as session:
        hosting = Hosting(
            client_id=client_id,
            service=service,
            username=username,
            password=encrypt_password(password)  # Always encrypt passwords
        )
        session.add(hosting)
        session.commit()
```

### 2. GUI Event Handling

```python
def setup_bindings(self):
    """Set up keyboard shortcuts and event bindings"""
    self.root.bind('<Control-n>', lambda e: self.new_client())
    self.root.bind('<Control-e>', lambda e: self.edit_client())
    self.root.bind('<Control-c>', lambda e: self.copy_to_clipboard())
    self.root.bind('<Delete>', lambda e: self.delete_client())
    self.client_tree.bind('<<TreeviewSelect>>', self.on_client_select)
```

### 3. Configuration Management

```python
# Loading settings
settings = get_settings()
theme = settings.get('theme', 'cosmo')
window_size = settings.get('window_size', '1000x700')

# Saving settings
save_setting('theme', new_theme)
save_setting('window_size', f'{width}x{height}')
```

## Development Guidelines for LLMs

### 1. Security Best Practices
- **Always encrypt passwords** using `encrypt_password()` before storing
- **Validate input** in all GUI forms and API endpoints
- **Use parameterized queries** through SQLAlchemy (already implemented)
- **Handle decryption errors** gracefully

### 2. GUI Development
- **Use ttkbootstrap widgets** for modern appearance
- **Follow existing naming conventions**: `snake_case` for variables, `PascalCase` for classes
- **Implement proper event handling** with try-catch blocks
- **Maintain responsive UI** - use threading for long operations

### 3. Database Operations
- **Use context managers** (`with get_session()`) for database sessions
- **Handle relationship loading** properly (lazy vs eager loading)
- **Implement proper error handling** for database operations
- **Use transactions** for multi-table operations

### 4. Code Organization
- **Separate concerns**: Keep GUI, database, and business logic separate
- **Use type hints** where possible
- **Follow existing patterns** for consistency
- **Add docstrings** for new functions and classes

## Common Tasks for LLMs

### Adding a New Field to Client
1. Update the model in `database/models.py`
2. Create migration script or handle schema updates
3. Update the GUI forms in `gui/dialogs.py`
4. Update the display in `gui/main_window.py`
5. Update copy-to-clipboard functionality

### Adding a New Dialog Window
1. Create new class inheriting from appropriate ttkbootstrap window
2. Implement `__init__`, layout, and event handlers
3. Add validation for form inputs
4. Handle save/cancel operations
5. Integrate with main window

### Adding API Endpoints
1. Add route to `api/server.py`
2. Implement proper request validation
3. Use database session management
4. Return appropriate HTTP status codes
5. Handle errors gracefully

## Testing Guidelines

### Unit Tests Structure
```python
def test_encryption():
    """Test password encryption/decryption"""
    password = "test_password_123"
    encrypted = encrypt_password(password)
    assert encrypted != password
    assert decrypt_password(encrypted) == password

def test_client_creation():
    """Test client model creation"""
    client = Client(name="Test Client", email="test@example.com")
    assert client.name == "Test Client"
    assert client.email == "test@example.com"
```

### GUI Testing Considerations
- **Mock database operations** in GUI tests
- **Test keyboard shortcuts** and event bindings
- **Verify widget states** after operations
- **Test error handling** in user interactions

## Build and Deployment

### Local Development
```bash
# Setup with uv (recommended)
uv sync --dev
uv run python src/main.py

# Setup with pip (alternative)
pip install -e .[dev]
python src/main.py
```

### Building Executables
```bash
# Using build script
uv run python scripts/build.py

# Manual PyInstaller
uv run pyinstaller client-data-manager.spec
```

## Common Issues and Solutions

### 1. Import Errors
- **Issue**: Module not found errors
- **Solution**: Check `PYTHONPATH` and package structure
- **LLM Note**: Always use relative imports within the package

### 2. Database Connection Issues
- **Issue**: SQLite database locked or permission errors
- **Solution**: Ensure proper session management and file permissions
- **LLM Note**: Always use context managers for database sessions

### 3. GUI Freezing
- **Issue**: Long operations blocking the UI
- **Solution**: Use threading for database operations
- **LLM Note**: Update UI elements from main thread only

### 4. Encryption Errors
- **Issue**: Cannot decrypt existing data
- **Solution**: Check key derivation and handle migration
- **LLM Note**: Never change encryption methods without migration plan

## Integration Points

### External Libraries
- **ttkbootstrap**: Modern tkinter themes and widgets
- **SQLAlchemy**: ORM and database operations
- **cryptography**: Fernet encryption for security
- **Flask**: Web API framework
- **PyInstaller**: Creating standalone executables

### Configuration Files
- `config/app_settings.json`: User preferences and settings
- `pyproject.toml`: Project metadata and dependencies
- `client-data-manager.spec`: PyInstaller build configuration

## Performance Considerations

### Database Optimization
- Use **eager loading** for related data when needed
- Implement **proper indexing** for search functionality
- **Batch operations** for multiple database changes
- **Connection pooling** for API endpoints

### GUI Responsiveness
- **Lazy loading** for large client lists
- **Virtual scrolling** for very large datasets
- **Debounced search** to avoid excessive database queries
- **Progress indicators** for long operations

## Security Model

### Data Protection
- **Encryption at rest**: Passwords encrypted with Fernet
- **No network transmission**: All data stored locally
- **Key derivation**: PBKDF2 with SHA-256
- **Secure deletion**: Overwrite sensitive data in memory

### Access Control
- **File system permissions**: Database file access control
- **No authentication**: Single-user desktop application
- **Audit trail**: Timestamps for data creation/modification

This guide should help LLMs understand the codebase structure and contribute effectively to the Client Data Manager project.
