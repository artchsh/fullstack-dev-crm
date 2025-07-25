# Client Data Manager

A modern, secure desktop application for managing client hosting, database, and website information.

## Features

- 🔐 **Secure Storage**: All sensitive data (passwords) are encrypted using industry-standard encryption
- 🎨 **Modern UI**: Beautiful, intuitive interface built with ttkbootstrap
- 📋 **Quick Copy**: One-click copying of client data to clipboard in human-readable format
- 🔍 **Smart Search**: Fast search and filtering capabilities
- 💾 **SQLAlchemy Database**: Reliable data persistence with SQLite
- 🌐 **Cross-Platform**: Works on Windows, macOS, and Linux

## What You Can Store

### Hosting Information
- Hosting service provider
- Service link/URL
- Login credentials
- Password (encrypted)
- Notes

### Database Information
- Database username
- Database name
- Database password (encrypted)

### Website Information
- Domain name
- Admin panel link
- Admin panel login
- Admin panel password (encrypted)

## Installation

### Prerequisites
- Python 3.8 or higher
- uv package manager (recommended) or pip

### Using uv (Recommended)
```bash
# Clone or download the project
cd client-data-manager

# Install dependencies
uv sync

# Run the application
uv run python src/main.py
```

### Using pip
```bash
# Clone or download the project
cd client-data-manager

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py
```

## Usage

### Adding a New Client
1. Click the "➕ New Client" button or use Ctrl+N
2. Fill in the client information (only name is required)
3. Click "💾 Save" to store the client data

### Editing Client Data
1. Select a client from the list
2. Click "✏️ Edit" or use Ctrl+E
3. Modify the information as needed
4. Click "💾 Save" to update

### Copying Data to Clipboard
- **Copy All Data**: Click "📋 Copy All Data" or use Ctrl+C to copy all client information
- **Copy Specific Sections**: Use the "Hosting", "Database", or "Website" buttons to copy only specific sections

### Searching Clients
- Use the search box at the top to find clients by name, domain, or hosting service
- Search is performed in real-time as you type

## Security

- All passwords are encrypted using Fernet (symmetric encryption)
- Database file is stored locally on your machine
- No data is transmitted over the internet
- Encryption keys are derived using PBKDF2 with SHA-256

## Keyboard Shortcuts

- **Ctrl+N**: New client
- **Ctrl+E**: Edit selected client
- **Ctrl+C**: Copy all data to clipboard
- **F5**: Refresh client list
- **Delete**: Delete selected client
- **Ctrl+Q**: Quit application

## File Structure

```
client-data-manager/
├── src/
│   ├── main.py              # Application entry point
│   ├── config/
│   │   └── settings.py      # Configuration settings
│   ├── database/
│   │   ├── models.py        # SQLAlchemy models
│   │   └── db_manager.py    # Database operations
│   ├── gui/
│   │   ├── main_window.py   # Main application window
│   │   └── dialogs.py       # Dialog windows
│   └── utils/
│       ├── encryption.py    # Encryption utilities
│       └── clipboard.py     # Clipboard operations
├── data/                    # Database storage (created automatically)
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

## Database

The application uses SQLite with SQLAlchemy ORM for data persistence. The database file is automatically created in the `data/` directory when you first run the application.

## Themes

The application uses the "cosmo" theme by default, providing a modern, clean appearance. The UI is designed to work well across different operating systems and screen sizes.

## Troubleshooting

### Common Issues

1. **Application won't start**: Make sure all dependencies are installed correctly
2. **Database errors**: Check that you have write permissions in the application directory
3. **Encryption errors**: If you see decryption errors, the database may be corrupted

### Getting Help

If you encounter issues:
1. Check the console output for error messages
2. Verify all dependencies are installed
3. Make sure you have proper file permissions

## Contributing

This is a personal project, but suggestions and improvements are welcome.

## License

This project is for personal/educational use. Please ensure you comply with all applicable laws and regulations when storing client data.

## Version History

- **v1.0.0**: Initial release with all core features
  - Secure client data management
  - Modern ttkbootstrap UI
  - SQLAlchemy database integration
  - Encryption for sensitive data
  - Clipboard functionality