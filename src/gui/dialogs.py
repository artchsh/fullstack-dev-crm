import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from typing import Optional
from database.models import ClientData


class ClientDialog:
    def __init__(self, parent: ttk.Window, title: str, client: Optional[ClientData] = None):
        self.parent = parent
        self.client = client
        self.result: Optional[ClientData] = None
        
        # Section visibility toggles
        self.hosting_visible = tk.BooleanVar(value=True)
        self.database_visible = tk.BooleanVar(value=True)
        self.website_visible = tk.BooleanVar(value=True)
        
        # Create dialog window with modern styling
        self.dialog = ttk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("750x650")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.center_dialog()
        
        # Setup dialog
        self.setup_dialog()
        
        # Pre-fill data if editing
        if client:
            self.populate_fields(client)
            # Auto-hide sections with no data
            self.auto_configure_sections(client)
        
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
    
    def auto_configure_sections(self, client: ClientData):
        """Auto-configure section visibility based on existing data"""
        # Show only sections that have data
        has_hosting = any([client.hosting_service, client.hosting_link, client.hosting_login, 
                          client.hosting_password, client.hosting_notes])
        has_database = any([client.db_username, client.db_name, client.db_password])
        has_website = any([client.domain, client.admin_panel_link, client.admin_panel_login, 
                          client.admin_panel_password, getattr(client, 'github_repo', '')])
        
        self.hosting_visible.set(has_hosting)
        self.database_visible.set(has_database)
        self.website_visible.set(has_website)
    
    def setup_dialog(self):
        """Setup the dialog interface with scrolling"""
        # Create main canvas and scrollbar for scrolling
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        
        # Create canvas
        self.canvas = tk.Canvas(main_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Main container
        main_container = ttk.Frame(self.scrollable_frame, padding=20)
        main_container.pack(fill=BOTH, expand=YES)
        
        # Configure grid weights
        main_container.columnconfigure(1, weight=1)
        
        # Title section
        title_frame = ttk.Frame(main_container)
        title_frame.grid(row=0, column=0, columnspan=2, sticky=(W, E), pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame,
            text="Client Information",
            font=("Segoe UI", 16, "bold")
        )
        title_label.pack(anchor=W)
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Enter client details. Use toggles to show/hide sections as needed.",
            font=("Segoe UI", 10),
            foreground="gray"
        )
        subtitle_label.pack(anchor=W, pady=(5, 0))
        
        row = 1
        
        # Client Name (Required)
        name_frame = ttk.LabelFrame(main_container, text="Basic Information", padding=15, bootstyle=PRIMARY)
        name_frame.grid(row=row, column=0, columnspan=2, sticky=(W, E), pady=(0, 15))
        name_frame.columnconfigure(1, weight=1)
        
        ttk.Label(name_frame, text="Client Name:*", font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, sticky=W, pady=(0, 10), padx=(0, 15))
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(name_frame, textvariable=self.name_var, width=40, font=("Segoe UI", 10))
        name_entry.grid(row=0, column=1, sticky=(W, E), pady=(0, 10))
        name_entry.focus()
        row += 1
        
        # Section toggles
        toggle_frame = ttk.Frame(main_container)
        toggle_frame.grid(row=row, column=0, columnspan=2, sticky=(W, E), pady=(0, 15))
        
        ttk.Label(toggle_frame, text="Sections to include:", font=("Segoe UI", 10, "bold")).pack(anchor=W, pady=(0, 5))
        
        toggles_container = ttk.Frame(toggle_frame)
        toggles_container.pack(anchor=W)
        
        hosting_check = ttk.Checkbutton(toggles_container, text="🌐 Hosting", variable=self.hosting_visible,
                                       command=self.update_sections, bootstyle=INFO)
        hosting_check.pack(side=LEFT, padx=(0, 20))
        
        database_check = ttk.Checkbutton(toggles_container, text="🗄️ Database", variable=self.database_visible,
                                        command=self.update_sections, bootstyle=SUCCESS)
        database_check.pack(side=LEFT, padx=(0, 20))
        
        website_check = ttk.Checkbutton(toggles_container, text="🌍 Website", variable=self.website_visible,
                                       command=self.update_sections, bootstyle=WARNING)
        website_check.pack(side=LEFT)
        row += 1
        
        # Hosting Section
        self.hosting_frame = ttk.LabelFrame(main_container, text="🌐 Hosting Information", 
                                           padding=15, bootstyle=INFO)
        self.hosting_frame.grid(row=row, column=0, columnspan=2, sticky=(W, E), pady=(0, 15))
        self.hosting_frame.columnconfigure(1, weight=1)
        self.hosting_row = row
        
        self.setup_hosting_section()
        row += 1
        
        # Database Section
        self.database_frame = ttk.LabelFrame(main_container, text="🗄️ Database Information", 
                                            padding=15, bootstyle=SUCCESS)
        self.database_frame.grid(row=row, column=0, columnspan=2, sticky=(W, E), pady=(0, 15))
        self.database_frame.columnconfigure(1, weight=1)
        self.database_row = row
        
        self.setup_database_section()
        row += 1
        
        # Website Section
        self.website_frame = ttk.LabelFrame(main_container, text="🌍 Website Information", 
                                           padding=15, bootstyle=WARNING)
        self.website_frame.grid(row=row, column=0, columnspan=2, sticky=(W, E), pady=(0, 20))
        self.website_frame.columnconfigure(1, weight=1)
        self.website_row = row
        
        self.setup_website_section()
        row += 1
        
        # Buttons with modern styling
        button_frame = ttk.Frame(main_container)
        button_frame.grid(row=row, column=0, columnspan=2, sticky=(W, E), pady=(20, 0))
        
        # Create button frame for right alignment
        btn_container = ttk.Frame(button_frame)
        btn_container.pack(side=RIGHT)
        
        ttk.Button(
            btn_container, 
            text="💾 Save", 
            command=self.save_client,
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
        
        # Initial section visibility update
        self.update_sections()
        
        # Bind keyboard shortcuts
        self.dialog.bind('<Return>', lambda e: self.save_client())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        self.dialog.bind('<Control-s>', lambda e: self.save_client())
        
        # Bind mouse wheel to canvas for scrolling
        self.bind_mousewheel()
    
    def bind_mousewheel(self):
        """Bind mouse wheel events for scrolling"""
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)
    
    def update_sections(self):
        """Update section visibility based on toggles"""
        if self.hosting_visible.get():
            self.hosting_frame.grid()
        else:
            self.hosting_frame.grid_remove()
            
        if self.database_visible.get():
            self.database_frame.grid()
        else:
            self.database_frame.grid_remove()
            
        if self.website_visible.get():
            self.website_frame.grid()
        else:
            self.website_frame.grid_remove()
        
        # Update scroll region
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def setup_hosting_section(self):
        """Setup hosting information section"""
        # Hosting Service
        ttk.Label(self.hosting_frame, text="Hosting Service:", font=("Segoe UI", 10)).grid(
            row=0, column=0, sticky=W, pady=(0, 10), padx=(0, 15))
        self.hosting_service_var = tk.StringVar()
        ttk.Entry(self.hosting_frame, textvariable=self.hosting_service_var, font=("Segoe UI", 10)).grid(
            row=0, column=1, sticky=(W, E), pady=(0, 10))
        
        # Hosting Link
        ttk.Label(self.hosting_frame, text="Service Link:", font=("Segoe UI", 10)).grid(
            row=1, column=0, sticky=W, pady=(0, 10), padx=(0, 15))
        self.hosting_link_var = tk.StringVar()
        ttk.Entry(self.hosting_frame, textvariable=self.hosting_link_var, font=("Segoe UI", 10)).grid(
            row=1, column=1, sticky=(W, E), pady=(0, 10))
        
        # Hosting Login
        ttk.Label(self.hosting_frame, text="Login/Email:", font=("Segoe UI", 10)).grid(
            row=2, column=0, sticky=W, pady=(0, 10), padx=(0, 15))
        self.hosting_login_var = tk.StringVar()
        ttk.Entry(self.hosting_frame, textvariable=self.hosting_login_var, font=("Segoe UI", 10)).grid(
            row=2, column=1, sticky=(W, E), pady=(0, 10))
        
        # Hosting Password
        ttk.Label(self.hosting_frame, text="Password:", font=("Segoe UI", 10)).grid(
            row=3, column=0, sticky=W, pady=(0, 10), padx=(0, 15))
        self.hosting_password_var = tk.StringVar()
        password_frame = ttk.Frame(self.hosting_frame)
        password_frame.grid(row=3, column=1, sticky=(W, E), pady=(0, 10))
        password_frame.columnconfigure(0, weight=1)
        
        self.hosting_password_entry = ttk.Entry(password_frame, textvariable=self.hosting_password_var, 
                                               show="*", font=("Segoe UI", 10))
        self.hosting_password_entry.grid(row=0, column=0, sticky=(W, E), padx=(0, 5))
        
        self.hosting_show_btn = ttk.Button(password_frame, text="👁", width=3,
                                          command=lambda: self.toggle_password(self.hosting_password_entry, self.hosting_show_btn))
        self.hosting_show_btn.grid(row=0, column=1)
        
        # Hosting Notes
        ttk.Label(self.hosting_frame, text="Notes:", font=("Segoe UI", 10)).grid(
            row=4, column=0, sticky=NW, pady=(0, 10), padx=(0, 15))
        notes_frame = ttk.Frame(self.hosting_frame)
        notes_frame.grid(row=4, column=1, sticky=(W, E), pady=(0, 10))
        notes_frame.columnconfigure(0, weight=1)
        
        self.hosting_notes_text = tk.Text(notes_frame, height=3, width=40, font=("Segoe UI", 10), wrap=tk.WORD)
        self.hosting_notes_text.grid(row=0, column=0, sticky=(W, E))
        
        notes_scrollbar = ttk.Scrollbar(notes_frame, orient="vertical", command=self.hosting_notes_text.yview)
        notes_scrollbar.grid(row=0, column=1, sticky=(N, S))
        self.hosting_notes_text.configure(yscrollcommand=notes_scrollbar.set)
    
    def setup_database_section(self):
        """Setup database information section"""
        # Database Username
        ttk.Label(self.database_frame, text="Username:", font=("Segoe UI", 10)).grid(
            row=0, column=0, sticky=W, pady=(0, 10), padx=(0, 15))
        self.db_username_var = tk.StringVar()
        ttk.Entry(self.database_frame, textvariable=self.db_username_var, font=("Segoe UI", 10)).grid(
            row=0, column=1, sticky=(W, E), pady=(0, 10))
        
        # Database Name
        ttk.Label(self.database_frame, text="Database Name:", font=("Segoe UI", 10)).grid(
            row=1, column=0, sticky=W, pady=(0, 10), padx=(0, 15))
        self.db_name_var = tk.StringVar()
        ttk.Entry(self.database_frame, textvariable=self.db_name_var, font=("Segoe UI", 10)).grid(
            row=1, column=1, sticky=(W, E), pady=(0, 10))
        
        # Database Password
        ttk.Label(self.database_frame, text="Password:", font=("Segoe UI", 10)).grid(
            row=2, column=0, sticky=W, pady=(0, 10), padx=(0, 15))
        self.db_password_var = tk.StringVar()
        db_password_frame = ttk.Frame(self.database_frame)
        db_password_frame.grid(row=2, column=1, sticky=(W, E), pady=(0, 10))
        db_password_frame.columnconfigure(0, weight=1)
        
        self.db_password_entry = ttk.Entry(db_password_frame, textvariable=self.db_password_var, 
                                          show="*", font=("Segoe UI", 10))
        self.db_password_entry.grid(row=0, column=0, sticky=(W, E), padx=(0, 5))
        
        self.db_show_btn = ttk.Button(db_password_frame, text="👁", width=3,
                                     command=lambda: self.toggle_password(self.db_password_entry, self.db_show_btn))
        self.db_show_btn.grid(row=0, column=1)
    
    def setup_website_section(self):
        """Setup website information section"""
        # Domain
        ttk.Label(self.website_frame, text="Domain:", font=("Segoe UI", 10)).grid(
            row=0, column=0, sticky=W, pady=(0, 10), padx=(0, 15))
        self.domain_var = tk.StringVar()
        ttk.Entry(self.website_frame, textvariable=self.domain_var, font=("Segoe UI", 10)).grid(
            row=0, column=1, sticky=(W, E), pady=(0, 10))
        
        # Admin Panel Link
        ttk.Label(self.website_frame, text="Admin Panel Link:", font=("Segoe UI", 10)).grid(
            row=1, column=0, sticky=W, pady=(0, 10), padx=(0, 15))
        self.admin_panel_link_var = tk.StringVar()
        ttk.Entry(self.website_frame, textvariable=self.admin_panel_link_var, font=("Segoe UI", 10)).grid(
            row=1, column=1, sticky=(W, E), pady=(0, 10))
        
        # Admin Panel Login
        ttk.Label(self.website_frame, text="Admin Panel Login:", font=("Segoe UI", 10)).grid(
            row=2, column=0, sticky=W, pady=(0, 10), padx=(0, 15))
        self.admin_panel_login_var = tk.StringVar()
        ttk.Entry(self.website_frame, textvariable=self.admin_panel_login_var, font=("Segoe UI", 10)).grid(
            row=2, column=1, sticky=(W, E), pady=(0, 10))
        
        # Admin Panel Password
        ttk.Label(self.website_frame, text="Admin Panel Password:", font=("Segoe UI", 10)).grid(
            row=3, column=0, sticky=W, pady=(0, 10), padx=(0, 15))
        self.admin_panel_password_var = tk.StringVar()
        admin_password_frame = ttk.Frame(self.website_frame)
        admin_password_frame.grid(row=3, column=1, sticky=(W, E), pady=(0, 10))
        admin_password_frame.columnconfigure(0, weight=1)
        
        self.admin_panel_password_entry = ttk.Entry(admin_password_frame, textvariable=self.admin_panel_password_var, 
                                                   show="*", font=("Segoe UI", 10))
        self.admin_panel_password_entry.grid(row=0, column=0, sticky=(W, E), padx=(0, 5))
        
        self.admin_show_btn = ttk.Button(admin_password_frame, text="👁", width=3,
                                        command=lambda: self.toggle_password(self.admin_panel_password_entry, self.admin_show_btn))
        self.admin_show_btn.grid(row=0, column=1)
        
        # GitHub Repository
        ttk.Label(self.website_frame, text="GitHub Repository:", font=("Segoe UI", 10)).grid(
            row=4, column=0, sticky=W, pady=(0, 10), padx=(0, 15))
        self.github_repo_var = tk.StringVar()
        ttk.Entry(self.website_frame, textvariable=self.github_repo_var, font=("Segoe UI", 10)).grid(
            row=4, column=1, sticky=(W, E), pady=(0, 10))
    
    def toggle_password(self, entry_widget, button_widget):
        """Toggle password visibility"""
        current_show = entry_widget.cget('show')
        if current_show == '*':
            entry_widget.configure(show='')
            button_widget.configure(text='🙈')
        else:
            entry_widget.configure(show='*')
            button_widget.configure(text='👁')
    
    def populate_fields(self, client: ClientData):
        """Populate fields with existing client data"""
        self.name_var.set(client.name or "")
        self.hosting_service_var.set(client.hosting_service or "")
        self.hosting_link_var.set(client.hosting_link or "")
        self.hosting_login_var.set(client.hosting_login or "")
        self.hosting_password_var.set(client.hosting_password or "")
        
        self.hosting_notes_text.delete(1.0, tk.END)
        self.hosting_notes_text.insert(1.0, client.hosting_notes or "")
        
        self.db_username_var.set(client.db_username or "")
        self.db_name_var.set(client.db_name or "")
        self.db_password_var.set(client.db_password or "")
        
        self.domain_var.set(client.domain or "")
        self.admin_panel_link_var.set(client.admin_panel_link or "")
        self.admin_panel_login_var.set(client.admin_panel_login or "")
        self.admin_panel_password_var.set(client.admin_panel_password or "")
        self.github_repo_var.set(getattr(client, 'github_repo', '') or "")
    
    def validate_input(self) -> bool:
        """Validate user input"""
        if not self.name_var.get().strip():
            messagebox.showerror("Validation Error", "Client name is required.")
            return False
        return True
    
    def save_client(self):
        """Save the client data"""
        if not self.validate_input():
            return
        
        # Get hosting notes
        hosting_notes = self.hosting_notes_text.get(1.0, tk.END).strip()
        
        # Create client data object
        client_data = ClientData(
            name=self.name_var.get().strip(),
            hosting_service=self.hosting_service_var.get().strip(),
            hosting_link=self.hosting_link_var.get().strip(),
            hosting_login=self.hosting_login_var.get().strip(),
            hosting_password=self.hosting_password_var.get().strip(),
            hosting_notes=hosting_notes,
            db_username=self.db_username_var.get().strip(),
            db_name=self.db_name_var.get().strip(),
            db_password=self.db_password_var.get().strip(),
            domain=self.domain_var.get().strip(),
            admin_panel_link=self.admin_panel_link_var.get().strip(),
            admin_panel_login=self.admin_panel_login_var.get().strip(),
            admin_panel_password=self.admin_panel_password_var.get().strip(),
            github_repo=self.github_repo_var.get().strip()
        )
        
        # If editing, preserve the ID and timestamps
        if self.client:
            client_data.id = self.client.id
            client_data.created_at = self.client.created_at
            client_data.updated_at = self.client.updated_at
        
        self.result = client_data
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel the dialog"""
        self.result = None
        self.dialog.destroy()


class PasswordDialog:
    def __init__(self, parent: ttk.Window, title: str = "Enter Password"):
        self.parent = parent
        self.result: Optional[str] = None
        
        # Create dialog window with modern styling
        self.dialog = ttk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("450x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.center_dialog()
        
        # Setup dialog
        self.setup_dialog()
        
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
        main_container = ttk.Frame(self.dialog, padding=30)
        main_container.pack(fill=BOTH, expand=YES)
        
        # Configure grid weights
        main_container.columnconfigure(1, weight=1)
        
        # Password frame
        password_frame = ttk.LabelFrame(main_container, text="Authentication", padding=20, bootstyle=PRIMARY)
        password_frame.grid(row=0, column=0, columnspan=2, sticky=(W, E), pady=(0, 20))
        password_frame.columnconfigure(1, weight=1)
        
        # Password field
        ttk.Label(password_frame, text="Password:", font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, sticky=W, padx=(0, 15))
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(password_frame, textvariable=self.password_var, 
                                  show="*", width=30, font=("Segoe UI", 10))
        password_entry.grid(row=0, column=1, sticky=(W, E))
        password_entry.focus()
        
        # Buttons
        button_frame = ttk.Frame(main_container)
        button_frame.grid(row=1, column=0, columnspan=2, sticky=(W, E))
        
        btn_container = ttk.Frame(button_frame)
        btn_container.pack(side=RIGHT)
        
        ttk.Button(
            btn_container, 
            text="✓ OK", 
            command=self.ok_clicked,
            bootstyle=SUCCESS,
            width=10
        ).pack(side=RIGHT, padx=(10, 0))
        
        ttk.Button(
            btn_container, 
            text="✗ Cancel", 
            command=self.cancel_clicked,
            bootstyle=(SECONDARY, OUTLINE),
            width=10
        ).pack(side=RIGHT)
        
        # Bind keyboard shortcuts
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
        self.dialog.bind('<Escape>', lambda e: self.cancel_clicked())
    
    def ok_clicked(self):
        """Handle OK button click"""
        self.result = self.password_var.get()
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """Handle Cancel button click"""
        self.result = None
        self.dialog.destroy()


def show_error_dialog(parent: ttk.Window, message: str):
    """Show an error dialog with modern styling"""
    messagebox.showerror("Error", message)


def show_info_dialog(parent: ttk.Window, message: str):
    """Show an information dialog with modern styling"""
    messagebox.showinfo("Information", message)


def show_warning_dialog(parent: ttk.Window, message: str):
    """Show a warning dialog with modern styling"""
    messagebox.showwarning("Warning", message)


def show_question_dialog(parent: ttk.Window, message: str) -> bool:
    """Show a yes/no question dialog with modern styling"""
    return messagebox.askyesno("Question", message)
