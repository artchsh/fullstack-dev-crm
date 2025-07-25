import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from typing import Optional
from config.app_settings import app_settings
from api.server import api_server


class SettingsDialog:
    def __init__(self, parent: ttk.Window):
        self.parent = parent
        self.result = False
        
        # Create dialog window
        self.dialog = ttk.Toplevel(parent)
        self.dialog.title("Settings")
        self.dialog.geometry("950x900")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.center_dialog()
        
        # Setup dialog
        self.setup_dialog()
        
        # Load current settings
        self.load_current_settings()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def center_dialog(self):
        """Center the dialog on the parent window"""
        self.dialog.update_idletasks()
        x = (self.parent.winfo_x() + (self.parent.winfo_width() // 2) - 
             (self.dialog.winfo_reqwidth() // 2))
        y = (self.parent.winfo_y() + (self.parent.winfo_height() // 2) - 
             (self.dialog.winfo_reqheight() // 2))
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_dialog(self):
        """Setup the dialog interface"""
        # Main container
        main_container = ttk.Frame(self.dialog, padding=20)
        main_container.pack(fill=BOTH, expand=YES)
        
        # Title
        title_label = ttk.Label(
            main_container,
            text="Application Settings",
            font=("Segoe UI", 16, "bold")
        )
        title_label.pack(anchor=W, pady=(0, 20))
        
        # Create notebook for settings sections
        self.notebook = ttk.Notebook(main_container, bootstyle=INFO)
        self.notebook.pack(fill=BOTH, expand=YES, pady=(0, 20))
        
        # API Settings Tab
        self.setup_api_tab()
        
        # UI Settings Tab
        self.setup_ui_tab()
        
        # Database Settings Tab
        self.setup_database_tab()
        
        # Button frame
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill=X, pady=(10, 0))
        
        # Buttons
        btn_container = ttk.Frame(button_frame)
        btn_container.pack(side=RIGHT)
        
        ttk.Button(
            btn_container,
            text="💾 Save",
            command=self.save_settings,
            bootstyle=SUCCESS,
            width=12
        ).pack(side=RIGHT, padx=(10, 0))
        
        ttk.Button(
            btn_container,
            text="❌ Cancel",
            command=self.cancel,
            bootstyle=(SECONDARY, OUTLINE),
            width=12
        ).pack(side=RIGHT)
        
        # Bind keyboard shortcuts
        self.dialog.bind('<Return>', lambda e: self.save_settings())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        self.dialog.bind('<Control-s>', lambda e: self.save_settings())
    
    def setup_api_tab(self):
        """Setup API settings tab"""
        api_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(api_frame, text="🌐 REST API")
        
        # API Enable/Disable
        enable_frame = ttk.LabelFrame(api_frame, text="API Status", padding=15, bootstyle=PRIMARY)
        enable_frame.pack(fill=X, pady=(0, 15))
        
        self.api_enabled_var = tk.BooleanVar()
        enable_check = ttk.Checkbutton(
            enable_frame,
            text="Enable REST API Server",
            variable=self.api_enabled_var,
            command=self.on_api_toggle,
            bootstyle=SUCCESS
        )
        enable_check.pack(anchor=W)
        
        info_label = ttk.Label(
            enable_frame,
            text="Enables remote access to client data via HTTP REST API",
            font=("Segoe UI", 9),
            foreground="gray"
        )
        info_label.pack(anchor=W, pady=(5, 0))
        
        # API Configuration
        self.config_frame = ttk.LabelFrame(api_frame, text="API Configuration", padding=15, bootstyle=INFO)
        self.config_frame.pack(fill=X, pady=(0, 15))
        
        # Host
        host_frame = ttk.Frame(self.config_frame)
        host_frame.pack(fill=X, pady=(0, 10))
        
        ttk.Label(host_frame, text="Host:", font=("Segoe UI", 10, "bold")).pack(side=LEFT)
        self.api_host_var = tk.StringVar()
        host_entry = ttk.Entry(host_frame, textvariable=self.api_host_var, width=20)
        host_entry.pack(side=LEFT, padx=(10, 0))
        
        ttk.Label(host_frame, text="(127.0.0.1 for local only, 0.0.0.0 for network access)", 
                 font=("Segoe UI", 9), foreground="gray").pack(side=LEFT, padx=(10, 0))
        
        # Port
        port_frame = ttk.Frame(self.config_frame)
        port_frame.pack(fill=X, pady=(0, 10))
        
        ttk.Label(port_frame, text="Port:", font=("Segoe UI", 10, "bold")).pack(side=LEFT)
        self.api_port_var = tk.StringVar()
        port_entry = ttk.Entry(port_frame, textvariable=self.api_port_var, width=10)
        port_entry.pack(side=LEFT, padx=(10, 0))
        
        # Access Key
        key_frame = ttk.Frame(self.config_frame)
        key_frame.pack(fill=X, pady=(0, 10))
        
        ttk.Label(key_frame, text="Access Key:", font=("Segoe UI", 10, "bold")).pack(side=LEFT)
        self.api_key_var = tk.StringVar()
        key_entry = ttk.Entry(key_frame, textvariable=self.api_key_var, width=30)
        key_entry.pack(side=LEFT, padx=(10, 0))
        
        ttk.Label(key_frame, text="(Required in requests as ?key=<access_key>)", 
                 font=("Segoe UI", 9), foreground="gray").pack(side=LEFT, padx=(10, 0))
        
        # API Status
        self.status_frame = ttk.LabelFrame(api_frame, text="Current Status", padding=15, bootstyle=WARNING)
        self.status_frame.pack(fill=X)
        
        self.status_label = ttk.Label(self.status_frame, text="API Server: Stopped", font=("Segoe UI", 10))
        self.status_label.pack(anchor=W)
        
        self.update_api_status()
    
    def setup_ui_tab(self):
        """Setup UI settings tab"""
        ui_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(ui_frame, text="🎨 Interface")
        
        # Display Options
        display_frame = ttk.LabelFrame(ui_frame, text="Display Options", padding=15, bootstyle=PRIMARY)
        display_frame.pack(fill=X, pady=(0, 15))
        
        self.show_empty_sections_var = tk.BooleanVar()
        empty_check = ttk.Checkbutton(
            display_frame,
            text="Show empty sections in client details",
            variable=self.show_empty_sections_var,
            bootstyle=INFO
        )
        empty_check.pack(anchor=W)
        
        info_label = ttk.Label(
            display_frame,
            text="When enabled, all sections (Hosting, Database, Website) are always visible",
            font=("Segoe UI", 9),
            foreground="gray"
        )
        info_label.pack(anchor=W, pady=(5, 0))
        
        # Theme Options
        theme_frame = ttk.LabelFrame(ui_frame, text="Theme", padding=15, bootstyle=INFO)
        theme_frame.pack(fill=X, pady=(0, 15))
        
        ttk.Label(theme_frame, text="Application Theme:", font=("Segoe UI", 10, "bold")).pack(anchor=W, pady=(0, 5))
        
        self.theme_var = tk.StringVar()
        themes = ["cosmo", "flatly", "litera", "minty", "pulse", "sandstone", "united", "yeti"]
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var, values=themes, 
                                  state="readonly", width=15)
        theme_combo.pack(anchor=W)
        
        # Auto-save
        auto_frame = ttk.LabelFrame(ui_frame, text="Auto-save", padding=15, bootstyle=SUCCESS)
        auto_frame.pack(fill=X)
        
        self.auto_save_var = tk.BooleanVar()
        auto_check = ttk.Checkbutton(
            auto_frame,
            text="Auto-save changes",
            variable=self.auto_save_var,
            bootstyle=SUCCESS
        )
        auto_check.pack(anchor=W)
    
    def setup_database_tab(self):
        """Setup database settings tab"""
        db_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(db_frame, text="🗄️ Database")
        
        # Backup Options
        backup_frame = ttk.LabelFrame(db_frame, text="Backup Settings", padding=15, bootstyle=PRIMARY)
        backup_frame.pack(fill=X, pady=(0, 15))
        
        self.backup_enabled_var = tk.BooleanVar()
        backup_check = ttk.Checkbutton(
            backup_frame,
            text="Enable automatic backups",
            variable=self.backup_enabled_var,
            bootstyle=INFO
        )
        backup_check.pack(anchor=W)
        
        # Backup interval
        interval_frame = ttk.Frame(backup_frame)
        interval_frame.pack(fill=X, pady=(10, 0))
        
        ttk.Label(interval_frame, text="Backup interval (hours):", font=("Segoe UI", 10)).pack(side=LEFT)
        self.backup_interval_var = tk.StringVar()
        interval_entry = ttk.Entry(interval_frame, textvariable=self.backup_interval_var, width=10)
        interval_entry.pack(side=LEFT, padx=(10, 0))
        
        # Database Info
        info_frame = ttk.LabelFrame(db_frame, text="Database Information", padding=15, bootstyle=INFO)
        info_frame.pack(fill=X)
        
        from config.settings import Config
        db_info = f"""
Database Location: {Config.get_database_path()}
Data Directory: {Config.get_data_dir()}
        """.strip()
        
        info_text = tk.Text(info_frame, height=3, font=("Consolas", 9), state="disabled", wrap=tk.WORD)
        info_text.pack(fill=X)
        info_text.config(state="normal")
        info_text.insert(1.0, db_info)
        info_text.config(state="disabled")
    
    def on_api_toggle(self):
        """Handle API enable/disable toggle"""
        enabled = self.api_enabled_var.get()
        
        # Enable/disable configuration fields
        for widget in self.config_frame.winfo_children():
            self._configure_widget_state(widget, "normal" if enabled else "disabled")
        
        self.update_api_status()
    
    def _configure_widget_state(self, widget, state):
        """Recursively configure widget state"""
        try:
            if isinstance(widget, (ttk.Entry, ttk.Combobox)):
                widget.configure(state=state)
        except:
            pass
        
        # Configure children
        for child in widget.winfo_children():
            self._configure_widget_state(child, state)
    
    def update_api_status(self):
        """Update API status display"""
        if api_server.is_running:
            info = api_server.get_api_info()
            status_text = f"API Server: Running on {info['host']}:{info['port']}"
            self.status_label.configure(foreground="green")
        else:
            status_text = "API Server: Stopped"
            self.status_label.configure(foreground="red")
        
        self.status_label.configure(text=status_text)
    
    def load_current_settings(self):
        """Load current settings into the form"""
        # API settings
        self.api_enabled_var.set(app_settings.is_api_enabled())
        self.api_host_var.set(app_settings.get_api_host())
        self.api_port_var.set(str(app_settings.get_api_port()))
        self.api_key_var.set(app_settings.get_api_key())
        
        # UI settings
        self.show_empty_sections_var.set(app_settings.show_empty_sections())
        self.theme_var.set(app_settings.get("ui.theme", "cosmo"))
        self.auto_save_var.set(app_settings.get("ui.auto_save", True))
        
        # Database settings
        self.backup_enabled_var.set(app_settings.get("database.backup_enabled", True))
        self.backup_interval_var.set(str(app_settings.get("database.backup_interval_hours", 24)))
        
        # Update API controls
        self.on_api_toggle()
    
    def save_settings(self):
        """Save settings"""
        try:
            # Validate port
            try:
                port = int(self.api_port_var.get())
                if not (1 <= port <= 65535):
                    raise ValueError("Port must be between 1 and 65535")
            except ValueError as e:
                messagebox.showerror("Invalid Port", f"Invalid port number: {e}")
                return
            
            # Validate backup interval
            try:
                interval = int(self.backup_interval_var.get())
                if interval < 1:
                    raise ValueError("Backup interval must be at least 1 hour")
            except ValueError as e:
                messagebox.showerror("Invalid Interval", f"Invalid backup interval: {e}")
                return
            
            # Save API settings
            api_was_enabled = app_settings.is_api_enabled()
            app_settings.set("api.enabled", self.api_enabled_var.get())
            app_settings.set("api.host", self.api_host_var.get())
            app_settings.set("api.port", port)
            app_settings.set("api.access_key", self.api_key_var.get())
            
            # Save UI settings
            app_settings.set("ui.show_empty_sections", self.show_empty_sections_var.get())
            app_settings.set("ui.theme", self.theme_var.get())
            app_settings.set("ui.auto_save", self.auto_save_var.get())
            
            # Save database settings
            app_settings.set("database.backup_enabled", self.backup_enabled_var.get())
            app_settings.set("database.backup_interval_hours", interval)
            
            self.result = True
            
            # Show restart message if API settings changed
            api_enabled_now = app_settings.is_api_enabled()
            if api_was_enabled != api_enabled_now:
                messagebox.showinfo(
                    "Settings Saved",
                    "Settings saved successfully!\n\nAPI server changes will take effect when you restart the application."
                )
            else:
                messagebox.showinfo("Settings Saved", "Settings saved successfully!")
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def cancel(self):
        """Cancel the dialog"""
        self.result = False
        self.dialog.destroy()


def show_settings_dialog(parent: ttk.Window) -> bool:
    """Show settings dialog and return True if settings were saved"""
    dialog = SettingsDialog(parent)
    return dialog.result
