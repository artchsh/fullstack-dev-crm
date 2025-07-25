import tkinter as tk
from typing import Dict, Any


def copy_to_clipboard(data: str, root: tk.Tk = None) -> bool:
    """Copy string data to clipboard using tkinter"""
    try:
        if root is None:
            # Create a temporary root window if none provided
            temp_root = tk.Tk()
            temp_root.withdraw()  # Hide the window
            temp_root.clipboard_clear()
            temp_root.clipboard_append(data)
            temp_root.update()  # Required to finalize clipboard operation
            temp_root.destroy()
        else:
            root.clipboard_clear()
            root.clipboard_append(data)
            root.update()
        return True
    except Exception as e:
        print(f"Failed to copy to clipboard: {e}")
        return False


def copy_client_data_to_clipboard(client_data, root: tk.Tk = None) -> bool:
    """Copy formatted client data to clipboard"""
    try:
        formatted_data = client_data.format_for_clipboard()
        return copy_to_clipboard(formatted_data, root)
    except Exception as e:
        print(f"Failed to copy client data to clipboard: {e}")
        return False


def copy_multiple_clients_to_clipboard(clients_data: list, root: tk.Tk = None) -> bool:
    """Copy formatted data for multiple clients to clipboard"""
    try:
        if not clients_data:
            return copy_to_clipboard("No clients selected.", root)
        
        formatted_sections = []
        for client in clients_data:
            formatted_sections.append(client.format_for_clipboard())
        
        all_data = f"""MULTIPLE CLIENTS DATA
{'=' * 60}
Total clients: {len(clients_data)}
{'=' * 60}

""" + f"\n\n{'-' * 60}\n\n".join(formatted_sections)
        
        return copy_to_clipboard(all_data, root)
    except Exception as e:
        print(f"Failed to copy multiple clients data to clipboard: {e}")
        return False


def copy_field_to_clipboard(field_value: str, root: tk.Tk = None) -> bool:
    """Copy a single field value to clipboard"""
    try:
        if not field_value:
            field_value = ""
        return copy_to_clipboard(field_value, root)
    except Exception as e:
        print(f"Failed to copy field to clipboard: {e}")
        return False


def get_clipboard_content(root: tk.Tk = None) -> str:
    """Get current clipboard content"""
    try:
        if root is None:
            temp_root = tk.Tk()
            temp_root.withdraw()
            content = temp_root.clipboard_get()
            temp_root.destroy()
            return content
        else:
            return root.clipboard_get()
    except Exception as e:
        print(f"Failed to get clipboard content: {e}")
        return ""