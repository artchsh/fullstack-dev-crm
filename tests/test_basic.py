"""
Basic tests for the client data manager package.
"""
import pytest
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_package_imports():
    """Test that the main modules can be imported."""
    try:
        from database import models
        from database import db_manager
        from utils import encryption
        from config import settings
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import modules: {e}")


def test_encryption_basic():
    """Test basic encryption functionality."""
    from utils.encryption import encrypt_password, decrypt_password
    
    test_password = "test_password_123"
    encrypted = encrypt_password(test_password)
    
    # Encrypted password should be different from original
    assert encrypted != test_password
    assert encrypted is not None
    assert len(encrypted) > 0
    
    # Decryption should return original password
    decrypted = decrypt_password(encrypted)
    assert decrypted == test_password


def test_database_models():
    """Test that database models can be created."""
    from database.models import Client, Hosting, Database, Website
    
    # Test creating a client instance
    client = Client(
        name="Test Client",
        email="test@example.com",
        phone="123-456-7890"
    )
    
    assert client.name == "Test Client"
    assert client.email == "test@example.com"
    assert client.phone == "123-456-7890"


def test_config_loading():
    """Test that configuration can be loaded."""
    from config.settings import get_settings
    
    # This should not raise an exception
    settings = get_settings()
    assert settings is not None
