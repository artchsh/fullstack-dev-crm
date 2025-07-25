import os
import json
from typing import Dict, Any
from pathlib import Path


class AppSettings:
    """Application settings manager"""
    
    def __init__(self):
        self.config_dir = Path("config")
        self.config_file = self.config_dir / "app_settings.json"
        self.config_dir.mkdir(exist_ok=True)
        
        # Default settings
        self.defaults = {
            "api": {
                "enabled": False,
                "port": 8080,
                "access_key": "client-manager-key-2025",
                "host": "127.0.0.1"
            },
            "ui": {
                "show_empty_sections": False,
                "theme": "cosmo",
                "auto_save": True
            },
            "database": {
                "backup_enabled": True,
                "backup_interval_hours": 24
            }
        }
        
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                # Merge with defaults to ensure all keys exist
                settings = self.defaults.copy()
                self._deep_update(settings, loaded)
                return settings
            except Exception as e:
                print(f"Error loading settings: {e}")
                return self.defaults.copy()
        return self.defaults.copy()
    
    def _deep_update(self, base_dict: Dict, update_dict: Dict):
        """Deep update dictionary"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get(self, key_path: str, default=None):
        """Get setting value using dot notation (e.g., 'api.enabled')"""
        keys = key_path.split('.')
        value = self.settings
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def set(self, key_path: str, value):
        """Set setting value using dot notation"""
        keys = key_path.split('.')
        current = self.settings
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
        self.save_settings()
    
    # Convenience methods for common settings
    def is_api_enabled(self) -> bool:
        return self.get("api.enabled", False)
    
    def get_api_port(self) -> int:
        return self.get("api.port", 8080)
    
    def get_api_key(self) -> str:
        return self.get("api.access_key", "client-manager-key-2025")
    
    def get_api_host(self) -> str:
        return self.get("api.host", "127.0.0.1")
    
    def show_empty_sections(self) -> bool:
        return self.get("ui.show_empty_sections", False)


# Global settings instance
app_settings = AppSettings()
