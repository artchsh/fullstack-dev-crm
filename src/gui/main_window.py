import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from typing import Optional, List
import threading
import webbrowser

from database.db_manager import DatabaseManager
from database.models import ClientData
from utils.clipboard import copy_client_data_to_clipboard
from gui.dialogs import ClientDialog
from config.app_settings import app_settings
from gui.settings_dialog import show_settings_dialog
from api.server import api_server
from gui.dialogs import ClientDialog
from config.settings import Config


class MainWindow:
    def __init__(self, root: ttk.Window):
        self.root = root
        self.root.title(f"{Config.APP_TITLE} v{Config.VERSION}")
        self.root.geometry(f"{Config.WINDOW_DEFAULT_WIDTH}x{Config.WINDOW_DEFAULT_HEIGHT}")
        self.root.minsize(Config.WINDOW_MIN_WIDTH, Config.WINDOW_MIN_HEIGHT)
        
        # Set the theme
        self.style = ttk.Style("cosmo")  # Modern, clean theme
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        
        # Initialize current client
        self.current_client: Optional[ClientData] = None
        
        # Setup GUI
        self.setup_menu()
        self.setup_main_interface()
        
        # Load initial data
        self.refresh_client_list()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_menu(self):
        """Create the menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Client", command=self.new_client, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing, accelerator="Ctrl+Q")
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Edit Client", command=self.edit_client, accelerator="Ctrl+E")
        edit_menu.add_command(label="Delete Client", command=self.delete_client, accelerator="Delete")
        edit_menu.add_separator()
        edit_menu.add_command(label="Copy All Data", command=self.copy_all_data, accelerator="Ctrl+C")
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Settings", command=self.show_settings, accelerator="Ctrl+,")
        tools_menu.add_separator()
        tools_menu.add_command(label="Refresh", command=self.refresh_client_list, accelerator="F5")
        tools_menu.add_separator()
        tools_menu.add_command(label="About", command=self.show_about)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.new_client())
        self.root.bind('<Control-e>', lambda e: self.edit_client())
        self.root.bind('<Control-c>', lambda e: self.copy_all_data())
        self.root.bind('<Control-q>', lambda e: self.on_closing())
        self.root.bind('<Control-comma>', lambda e: self.show_settings())
        self.root.bind('<F5>', lambda e: self.refresh_client_list())
        self.root.bind('<Delete>', lambda e: self.delete_client())
    
    def setup_main_interface(self):
        """Setup the main interface"""
        # Create main container with padding
        main_container = ttk.Frame(self.root, padding=15)
        main_container.pack(fill=BOTH, expand=YES)
        
        # Configure grid weights
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(1, weight=1)
        
        # Title and stats
        self.setup_header(main_container)
        
        # Main content area
        content_frame = ttk.Frame(main_container)
        content_frame.grid(row=1, column=0, columnspan=2, sticky=(W, E, N, S), pady=(10, 0))
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Left panel - Client list
        self.setup_client_list_panel(content_frame)
        
        # Right panel - Client details
        self.setup_details_panel(content_frame)
        
        # Status bar
        self.setup_status_bar(main_container)
    
    def setup_header(self, parent):
        """Setup header with title and search"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(W, E), pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)
        
        # App title
        title_label = ttk.Label(
            header_frame, 
            text="Client Data Manager", 
            font=("Segoe UI", 18, "bold")
        )
        title_label.grid(row=0, column=0, sticky=W)
        
        # Client count
        self.client_count_label = ttk.Label(
            header_frame, 
            text="0 clients", 
            font=("Segoe UI", 10),
            foreground="gray"
        )
        self.client_count_label.grid(row=0, column=1, sticky=E)
        
        # Search frame
        search_frame = ttk.Frame(header_frame)
        search_frame.grid(row=1, column=0, columnspan=2, sticky=(W, E), pady=(10, 0))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Search:", font=("Segoe UI", 10)).grid(row=0, column=0, padx=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            search_frame, 
            textvariable=self.search_var,
            font=("Segoe UI", 10),
            width=30
        )
        self.search_entry.grid(row=0, column=1, sticky=(W, E), padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', self.on_search)
        
        # Search buttons
        ttk.Button(
            search_frame, 
            text="Clear", 
            command=self.clear_search,
            bootstyle=OUTLINE
        ).grid(row=0, column=2)
    
    def setup_client_list_panel(self, parent):
        """Setup the client list panel"""
        # Client list frame with modern styling
        list_panel = ttk.LabelFrame(
            parent, 
            text="Clients", 
            padding=15,
            bootstyle=PRIMARY
        )
        list_panel.grid(row=0, column=0, sticky=(W, E, N, S), padx=(0, 15))
        list_panel.columnconfigure(0, weight=1)
        list_panel.rowconfigure(1, weight=1)
        
        # Quick actions frame
        actions_frame = ttk.Frame(list_panel)
        actions_frame.grid(row=0, column=0, sticky=(W, E), pady=(0, 10))
        
        # Action buttons with modern styling
        ttk.Button(
            actions_frame, 
            text="➕ New Client", 
            command=self.new_client,
            bootstyle=SUCCESS,
            width=15
        ).pack(side=LEFT, padx=(0, 5))
        
        ttk.Button(
            actions_frame, 
            text="✏️ Edit", 
            command=self.edit_client,
            bootstyle=INFO,
            width=12
        ).pack(side=LEFT, padx=(0, 5))
        
        ttk.Button(
            actions_frame, 
            text="🗑️ Delete", 
            command=self.delete_client,
            bootstyle=DANGER,
            width=12
        ).pack(side=LEFT)
        
        # Client listbox with modern styling
        listbox_frame = ttk.Frame(list_panel)
        listbox_frame.grid(row=1, column=0, sticky=(W, E, N, S))
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)
        
        # Use Treeview instead of Listbox for better appearance
        self.client_tree = ttk.Treeview(
            listbox_frame,
            columns=('domain',),
            show='tree headings',
            height=15
        )
        self.client_tree.heading('#0', text='Client Name', anchor=W)
        self.client_tree.heading('domain', text='Domain', anchor=W)
        self.client_tree.column('#0', width=200, minwidth=150)
        self.client_tree.column('domain', width=150, minwidth=100)
        
        self.client_tree.grid(row=0, column=0, sticky=(W, E, N, S))
        self.client_tree.bind('<<TreeviewSelect>>', self.on_client_select)
        
        # Scrollbar for treeview
        tree_scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.client_tree.yview)
        tree_scrollbar.grid(row=0, column=1, sticky=(N, S))
        self.client_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Store client data for easy access
        self.clients: List[ClientData] = []
    
    def setup_details_panel(self, parent):
        """Setup the client details panel"""
        # Details frame with modern styling
        details_panel = ttk.LabelFrame(
            parent, 
            text="Client Details", 
            padding=15,
            bootstyle=SECONDARY
        )
        details_panel.grid(row=0, column=1, sticky=(W, E, N, S))
        details_panel.columnconfigure(0, weight=1)
        details_panel.rowconfigure(1, weight=1)
        
        # Copy actions frame
        copy_frame = ttk.Frame(details_panel)
        copy_frame.grid(row=0, column=0, sticky=(W, E), pady=(0, 15))
        
        # Main copy button
        ttk.Button(
            copy_frame, 
            text="📋 Copy All Data", 
            command=self.copy_all_data,
            bootstyle=(SUCCESS, OUTLINE),
            width=20
        ).pack(side=LEFT, padx=(0, 10))
        
        # Quick copy buttons
        ttk.Button(
            copy_frame, 
            text="Hosting", 
            command=self.copy_hosting_data,
            bootstyle=OUTLINE,
            width=10
        ).pack(side=LEFT, padx=(0, 5))
        
        ttk.Button(
            copy_frame, 
            text="Database", 
            command=self.copy_database_data,
            bootstyle=OUTLINE,
            width=10
        ).pack(side=LEFT, padx=(0, 5))
        
        ttk.Button(
            copy_frame, 
            text="Website", 
            command=self.copy_website_data,
            bootstyle=OUTLINE,
            width=10
        ).pack(side=LEFT, padx=(0, 5))
        
        # Quick action buttons
        action_frame = ttk.Frame(copy_frame)
        action_frame.pack(side=RIGHT)
        
        self.go_to_website_btn = ttk.Button(
            action_frame,
            text="🌐 Go to Website",
            command=self.go_to_website,
            bootstyle=(INFO, OUTLINE),
            width=15
        )
        self.go_to_website_btn.pack(side=LEFT, padx=(0, 5))
        
        self.go_to_admin_btn = ttk.Button(
            action_frame,
            text="⚙️ Go to Admin",
            command=self.go_to_admin,
            bootstyle=(WARNING, OUTLINE),
            width=15
        )
        self.go_to_admin_btn.pack(side=LEFT)
        
        # Create notebook for organized display
        self.notebook = ttk.Notebook(details_panel, bootstyle=INFO)
        self.notebook.grid(row=1, column=0, sticky=(W, E, N, S))
        
        # Hosting tab
        self.setup_hosting_tab()
        
        # Database tab
        self.setup_database_tab()
        
        # Website tab
        self.setup_website_tab()
    
    def setup_hosting_tab(self):
        """Setup the hosting information tab"""
        self.hosting_frame = ttk.Frame(self.notebook, padding=20)
        self.hosting_tab_id = self.notebook.add(self.hosting_frame, text="🌐 Hosting")
        
        # Configure grid
        self.hosting_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Service
        ttk.Label(self.hosting_frame, text="Hosting Service:", font=("Segoe UI", 10, "bold")).grid(
            row=row, column=0, sticky=W, pady=(0, 10), padx=(0, 15))
        self.hosting_service_var = tk.StringVar()
        service_entry = ttk.Entry(self.hosting_frame, textvariable=self.hosting_service_var, 
                                 state="readonly", font=("Segoe UI", 10))
        service_entry.grid(row=row, column=1, sticky=(W, E), pady=(0, 10))
        row += 1
        
        # Link
        ttk.Label(self.hosting_frame, text="Service Link:", font=("Segoe UI", 10, "bold")).grid(
            row=row, column=0, sticky=W, pady=(0, 10), padx=(0, 15))
        self.hosting_link_var = tk.StringVar()
        link_entry = ttk.Entry(self.hosting_frame, textvariable=self.hosting_link_var, 
                              state="readonly", font=("Segoe UI", 10))
        link_entry.grid(row=row, column=1, sticky=(W, E), pady=(0, 10))
        row += 1
        
        # Login/Email
        ttk.Label(self.hosting_frame, text="Login/Email:", font=("Segoe UI", 10, "bold")).grid(
            row=row, column=0, sticky=W, pady=(0, 10), padx=(0, 15))
        self.hosting_login_var = tk.StringVar()
        login_entry = ttk.Entry(self.hosting_frame, textvariable=self.hosting_login_var, 
                               state="readonly", font=("Segoe UI", 10))
        login_entry.grid(row=row, column=1, sticky=(W, E), pady=(0, 10))
        row += 1
        
        # Password
        ttk.Label(self.hosting_frame, text="Password:", font=("Segoe UI", 10, "bold")).grid(
            row=row, column=0, sticky=W, pady=(0, 10), padx=(0, 15))
        self.hosting_password_var = tk.StringVar()
        password_frame = ttk.Frame(self.hosting_frame)
        password_frame.grid(row=row, column=1, sticky=(W, E), pady=(0, 10))
        password_frame.columnconfigure(0, weight=1)
        
        self.hosting_password_entry = ttk.Entry(password_frame, textvariable=self.hosting_password_var, 
                                               state="readonly", show="*", font=("Segoe UI", 10))
        self.hosting_password_entry.grid(row=0, column=0, sticky=(W, E), padx=(0, 5))
        
        self.hosting_show_btn = ttk.Button(password_frame, text="👁", width=3,
                                          command=lambda: self.toggle_password(self.hosting_password_entry, self.hosting_show_btn))
        self.hosting_show_btn.grid(row=0, column=1)
        row += 1
        
        # Notes
        ttk.Label(self.hosting_frame, text="Notes:", font=("Segoe UI", 10, "bold")).grid(
            row=row, column=0, sticky=NW, pady=(0, 10), padx=(0, 15))
        notes_frame = ttk.Frame(self.hosting_frame)
        notes_frame.grid(row=row, column=1, sticky=(W, E, N, S), pady=(0, 10))
        notes_frame.columnconfigure(0, weight=1)
        notes_frame.rowconfigure(0, weight=1)
        
        self.hosting_notes_text = tk.Text(notes_frame, height=4, state="disabled", 
                                         font=("Segoe UI", 10), wrap=tk.WORD)
        self.hosting_notes_text.grid(row=0, column=0, sticky=(W, E, N, S))
        
        notes_scrollbar = ttk.Scrollbar(notes_frame, orient="vertical", command=self.hosting_notes_text.yview)
        notes_scrollbar.grid(row=0, column=1, sticky=(N, S))
        self.hosting_notes_text.configure(yscrollcommand=notes_scrollbar.set)
        
        self.hosting_frame.rowconfigure(row, weight=1)
    
    def setup_database_tab(self):
        """Setup the database information tab"""
        database_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(database_frame, text="🗄️ Database")
        
        # Configure grid
        database_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Username
        ttk.Label(database_frame, text="Username:", font=("Segoe UI", 10, "bold")).grid(
            row=row, column=0, sticky=W, pady=(0, 15), padx=(0, 15))
        self.db_username_var = tk.StringVar()
        username_entry = ttk.Entry(database_frame, textvariable=self.db_username_var, 
                                  state="readonly", font=("Segoe UI", 10))
        username_entry.grid(row=row, column=1, sticky=(W, E), pady=(0, 15))
        row += 1
        
        # Database Name
        ttk.Label(database_frame, text="Database Name:", font=("Segoe UI", 10, "bold")).grid(
            row=row, column=0, sticky=W, pady=(0, 15), padx=(0, 15))
        self.db_name_var = tk.StringVar()
        dbname_entry = ttk.Entry(database_frame, textvariable=self.db_name_var, 
                                state="readonly", font=("Segoe UI", 10))
        dbname_entry.grid(row=row, column=1, sticky=(W, E), pady=(0, 15))
        row += 1
        
        # Password
        ttk.Label(database_frame, text="Password:", font=("Segoe UI", 10, "bold")).grid(
            row=row, column=0, sticky=W, pady=(0, 15), padx=(0, 15))
        self.db_password_var = tk.StringVar()
        db_password_frame = ttk.Frame(database_frame)
        db_password_frame.grid(row=row, column=1, sticky=(W, E), pady=(0, 15))
        db_password_frame.columnconfigure(0, weight=1)
        
        self.db_password_entry = ttk.Entry(db_password_frame, textvariable=self.db_password_var, 
                                          state="readonly", show="*", font=("Segoe UI", 10))
        self.db_password_entry.grid(row=0, column=0, sticky=(W, E), padx=(0, 5))
        
        self.db_show_btn = ttk.Button(db_password_frame, text="👁", width=3,
                                     command=lambda: self.toggle_password(self.db_password_entry, self.db_show_btn))
        self.db_show_btn.grid(row=0, column=1)
    
    def setup_website_tab(self):
        """Setup the website information tab"""
        website_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(website_frame, text="🌍 Website")
        
        # Configure grid
        website_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Domain
        ttk.Label(website_frame, text="Domain:", font=("Segoe UI", 10, "bold")).grid(
            row=row, column=0, sticky=W, pady=(0, 15), padx=(0, 15))
        self.domain_var = tk.StringVar()
        domain_entry = ttk.Entry(website_frame, textvariable=self.domain_var, 
                                state="readonly", font=("Segoe UI", 10))
        domain_entry.grid(row=row, column=1, sticky=(W, E), pady=(0, 15))
        row += 1
        
        # Admin Panel Link
        ttk.Label(website_frame, text="Admin Panel Link:", font=("Segoe UI", 10, "bold")).grid(
            row=row, column=0, sticky=W, pady=(0, 15), padx=(0, 15))
        self.admin_panel_link_var = tk.StringVar()
        panel_link_entry = ttk.Entry(website_frame, textvariable=self.admin_panel_link_var, 
                                    state="readonly", font=("Segoe UI", 10))
        panel_link_entry.grid(row=row, column=1, sticky=(W, E), pady=(0, 15))
        row += 1
        
        # Admin Panel Login
        ttk.Label(website_frame, text="Admin Panel Login:", font=("Segoe UI", 10, "bold")).grid(
            row=row, column=0, sticky=W, pady=(0, 15), padx=(0, 15))
        self.admin_panel_login_var = tk.StringVar()
        panel_login_entry = ttk.Entry(website_frame, textvariable=self.admin_panel_login_var, 
                                     state="readonly", font=("Segoe UI", 10))
        panel_login_entry.grid(row=row, column=1, sticky=(W, E), pady=(0, 15))
        row += 1
        
        # Admin Panel Password
        ttk.Label(website_frame, text="Admin Panel Password:", font=("Segoe UI", 10, "bold")).grid(
            row=row, column=0, sticky=W, pady=(0, 15), padx=(0, 15))
        self.admin_panel_password_var = tk.StringVar()
        admin_password_frame = ttk.Frame(website_frame)
        admin_password_frame.grid(row=row, column=1, sticky=(W, E), pady=(0, 15))
        admin_password_frame.columnconfigure(0, weight=1)
        
        self.admin_panel_password_entry = ttk.Entry(admin_password_frame, textvariable=self.admin_panel_password_var, 
                                                   state="readonly", show="*", font=("Segoe UI", 10))
        self.admin_panel_password_entry.grid(row=0, column=0, sticky=(W, E), padx=(0, 5))
        
        self.admin_show_btn = ttk.Button(admin_password_frame, text="👁", width=3,
                                        command=lambda: self.toggle_password(self.admin_panel_password_entry, self.admin_show_btn))
        self.admin_show_btn.grid(row=0, column=1)
        row += 1
        
        # GitHub Repository
        ttk.Label(website_frame, text="GitHub Repository:", font=("Segoe UI", 10, "bold")).grid(
            row=row, column=0, sticky=W, pady=(0, 15), padx=(0, 15))
        self.github_repo_var = tk.StringVar()
        github_entry = ttk.Entry(website_frame, textvariable=self.github_repo_var, 
                                state="readonly", font=("Segoe UI", 10))
        github_entry.grid(row=row, column=1, sticky=(W, E), pady=(0, 15))
    
    def setup_status_bar(self, parent):
        """Setup status bar"""
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        status_bar = ttk.Label(
            parent, 
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=W,
            font=("Segoe UI", 9)
        )
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(W, E), pady=(10, 0))
    
    def toggle_password(self, entry_widget, button_widget):
        """Toggle password visibility"""
        current_show = entry_widget.cget('show')
        if current_show == '*':
            entry_widget.configure(show='')
            button_widget.configure(text='🙈')
        else:
            entry_widget.configure(show='*')
            button_widget.configure(text='👁')
    
    def refresh_client_list(self):
        """Refresh the client list from database"""
        def load_clients():
            try:
                self.status_var.set("Loading clients...")
                self.clients = self.db_manager.get_all_clients()
                self.root.after(0, lambda: self.update_client_tree(self.clients))
                self.root.after(0, lambda: self.update_client_count())
                self.root.after(0, lambda: self.status_var.set("Ready"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load clients: {e}"))
                self.root.after(0, lambda: self.status_var.set("Error loading clients"))
        
        # Load clients in background thread
        threading.Thread(target=load_clients, daemon=True).start()
    
    def update_client_tree(self, clients: List[ClientData]):
        """Update the client tree with given clients"""
        # Clear existing items
        for item in self.client_tree.get_children():
            self.client_tree.delete(item)
        
        # Add clients
        for client in clients:
            domain_text = client.domain or "No domain"
            self.client_tree.insert('', 'end', text=client.name, values=(domain_text,))
    
    def update_client_count(self):
        """Update the client count display"""
        count = len(self.clients)
        self.client_count_label.configure(text=f"{count} client{'s' if count != 1 else ''}")
    
    def on_client_select(self, event):
        """Handle client selection"""
        selection = self.client_tree.selection()
        if selection:
            item = selection[0]
            index = self.client_tree.index(item)
            
            # Get the actual clients list being displayed
            clients_to_display = self.get_current_displayed_clients()
            if index < len(clients_to_display):
                self.current_client = clients_to_display[index]
                self.display_client_details(self.current_client)
    
    def get_current_displayed_clients(self) -> List[ClientData]:
        """Get the currently displayed clients (filtered or all)"""
        search_term = self.search_var.get().strip()
        if search_term:
            return self.db_manager.search_clients(search_term)
        return self.clients
    
    def display_client_details(self, client: ClientData):
        """Display client details in the details panel"""
        # Hosting details
        self.hosting_service_var.set(client.hosting_service or "")
        self.hosting_link_var.set(client.hosting_link or "")
        self.hosting_login_var.set(client.hosting_login or "")
        self.hosting_password_var.set(client.hosting_password or "")
        
        self.hosting_notes_text.config(state="normal")
        self.hosting_notes_text.delete(1.0, tk.END)
        self.hosting_notes_text.insert(1.0, client.hosting_notes or "")
        self.hosting_notes_text.config(state="disabled")
        
        # Database details
        self.db_username_var.set(client.db_username or "")
        self.db_name_var.set(client.db_name or "")
        self.db_password_var.set(client.db_password or "")
        
        # Website details
        self.domain_var.set(client.domain or "")
        self.admin_panel_link_var.set(client.admin_panel_link or "")
        self.admin_panel_login_var.set(client.admin_panel_login or "")
        self.admin_panel_password_var.set(client.admin_panel_password or "")
        self.github_repo_var.set(getattr(client, 'github_repo', '') or "")
        
        # Update action buttons and tab visibility
        self.update_action_buttons()
        self.update_tab_visibility()
        
        self.status_var.set(f"Viewing: {client.name}")
    
    def on_search(self, event):
        """Handle search input"""
        search_term = self.search_var.get().strip()
        if search_term:
            filtered_clients = self.db_manager.search_clients(search_term)
            self.update_client_tree(filtered_clients)
        else:
            self.update_client_tree(self.clients)
    
    def clear_search(self):
        """Clear search and show all clients"""
        self.search_var.set("")
        self.update_client_tree(self.clients)
    
    def new_client(self):
        """Create a new client"""
        dialog = ClientDialog(self.root, "New Client")
        if dialog.result:
            try:
                self.status_var.set("Creating client...")
                client_id = self.db_manager.insert_client(dialog.result)
                dialog.result.id = client_id
                messagebox.showinfo("Success", "Client created successfully!")
                self.refresh_client_list()
                self.status_var.set("Client created successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create client: {e}")
                self.status_var.set("Error creating client")
    
    def edit_client(self):
        """Edit the selected client"""
        if not self.current_client:
            messagebox.showwarning("Warning", "Please select a client to edit.")
            return
        
        dialog = ClientDialog(self.root, "Edit Client", self.current_client)
        if dialog.result:
            try:
                self.status_var.set("Updating client...")
                success = self.db_manager.update_client(dialog.result)
                if success:
                    messagebox.showinfo("Success", "Client updated successfully!")
                    self.refresh_client_list()
                    self.display_client_details(dialog.result)
                    self.current_client = dialog.result
                    self.status_var.set("Client updated successfully")
                else:
                    messagebox.showerror("Error", "Failed to update client.")
                    self.status_var.set("Error updating client")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update client: {e}")
                self.status_var.set("Error updating client")
    
    def delete_client(self):
        """Delete the selected client"""
        if not self.current_client:
            messagebox.showwarning("Warning", "Please select a client to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete '{self.current_client.name}'?\n\nThis action cannot be undone."):
            try:
                self.status_var.set("Deleting client...")
                success = self.db_manager.delete_client(self.current_client.id)
                if success:
                    messagebox.showinfo("Success", "Client deleted successfully!")
                    self.refresh_client_list()
                    self.current_client = None
                    self.clear_client_details()
                    self.status_var.set("Client deleted successfully")
                else:
                    messagebox.showerror("Error", "Failed to delete client.")
                    self.status_var.set("Error deleting client")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete client: {e}")
                self.status_var.set("Error deleting client")
    
    def clear_client_details(self):
        """Clear all client detail fields"""
        # Clear all variables
        for var in [self.hosting_service_var, self.hosting_link_var, self.hosting_login_var,
                   self.hosting_password_var, self.db_username_var, self.db_name_var,
                   self.db_password_var, self.domain_var, self.admin_panel_link_var,
                   self.admin_panel_login_var, self.admin_panel_password_var, self.github_repo_var]:
            var.set("")
        
        # Clear notes text
        self.hosting_notes_text.config(state="normal")
        self.hosting_notes_text.delete(1.0, tk.END)
        self.hosting_notes_text.config(state="disabled")
        
        self.status_var.set("Ready")
    
    def copy_all_data(self):
        """Copy all client data to clipboard"""
        if not self.current_client:
            messagebox.showwarning("Warning", "Please select a client first.")
            return
        
        try:
            success = copy_client_data_to_clipboard(self.current_client, self.root)
            if success:
                messagebox.showinfo("Success", "All client data copied to clipboard!")
                self.status_var.set("Data copied to clipboard")
            else:
                messagebox.showerror("Error", "Failed to copy data to clipboard.")
                self.status_var.set("Error copying data")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy data: {e}")
            self.status_var.set("Error copying data")
    
    def copy_hosting_data(self):
        """Copy hosting data to clipboard"""
        if not self.current_client:
            messagebox.showwarning("Warning", "Please select a client first.")
            return
        
        hosting_data = f"""HOSTING INFORMATION - {self.current_client.name}
Service: {self.current_client.hosting_service or 'N/A'}
Link: {self.current_client.hosting_link or 'N/A'}
Login/Email: {self.current_client.hosting_login or 'N/A'}
Password: {self.current_client.hosting_password or 'N/A'}
Notes: {self.current_client.hosting_notes or 'N/A'}"""
        
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(hosting_data)
            self.root.update()
            messagebox.showinfo("Success", "Hosting data copied to clipboard!")
            self.status_var.set("Hosting data copied")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy hosting data: {e}")
            self.status_var.set("Error copying hosting data")
    
    def copy_database_data(self):
        """Copy database data to clipboard"""
        if not self.current_client:
            messagebox.showwarning("Warning", "Please select a client first.")
            return
        
        database_data = f"""DATABASE INFORMATION - {self.current_client.name}
Username: {self.current_client.db_username or 'N/A'}
Database Name: {self.current_client.db_name or 'N/A'}
Password: {self.current_client.db_password or 'N/A'}"""
        
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(database_data)
            self.root.update()
            messagebox.showinfo("Success", "Database data copied to clipboard!")
            self.status_var.set("Database data copied")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy database data: {e}")
            self.status_var.set("Error copying database data")
    
    def copy_website_data(self):
        """Copy website data to clipboard"""
        if not self.current_client:
            messagebox.showwarning("Warning", "Please select a client first.")
            return
        
        website_data = f"""WEBSITE INFORMATION - {self.current_client.name}
Domain: {self.current_client.domain or 'N/A'}
Admin Panel Link: {self.current_client.admin_panel_link or 'N/A'}
Admin Panel Login: {self.current_client.admin_panel_login or 'N/A'}
Admin Panel Password: {self.current_client.admin_panel_password or 'N/A'}
GitHub Repository: {getattr(self.current_client, 'github_repo', '') or 'N/A'}"""
        
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(website_data)
            self.root.update()
            messagebox.showinfo("Success", "Website data copied to clipboard!")
            self.status_var.set("Website data copied")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy website data: {e}")
            self.status_var.set("Error copying website data")
    
    def go_to_website(self):
        """Open website in browser"""
        if not self.current_client:
            messagebox.showwarning("Warning", "Please select a client first.")
            return
        
        domain = self.current_client.domain
        if not domain:
            messagebox.showwarning("Warning", "No website domain specified for this client.")
            return
        
        try:
            # Add protocol if not present
            if not domain.startswith(('http://', 'https://')):
                domain = 'https://' + domain
            
            webbrowser.open(domain)
            self.status_var.set(f"Opened {domain} in browser")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open website: {e}")
    
    def go_to_admin(self):
        """Open admin panel in browser"""
        if not self.current_client:
            messagebox.showwarning("Warning", "Please select a client first.")
            return
        
        admin_link = self.current_client.admin_panel_link
        if not admin_link:
            messagebox.showwarning("Warning", "No admin panel link specified for this client.")
            return
        
        try:
            # Add protocol if not present
            if not admin_link.startswith(('http://', 'https://')):
                admin_link = 'https://' + admin_link
            
            webbrowser.open(admin_link)
            self.status_var.set(f"Opened admin panel in browser")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open admin panel: {e}")
    
    def update_action_buttons(self):
        """Update action button states based on current client"""
        if self.current_client:
            # Enable/disable website button
            has_domain = bool(self.current_client.domain)
            self.go_to_website_btn.configure(state="normal" if has_domain else "disabled")
            
            # Enable/disable admin button
            has_admin = bool(self.current_client.admin_panel_link)
            self.go_to_admin_btn.configure(state="normal" if has_admin else "disabled")
        else:
            # Disable both buttons when no client selected
            self.go_to_website_btn.configure(state="disabled")
            self.go_to_admin_btn.configure(state="disabled")
    
    def update_tab_visibility(self):
        """Update tab visibility based on client data and settings"""
        if not self.current_client:
            return
        
        # Check if we should show empty sections
        show_empty = app_settings.show_empty_sections()
        
        if show_empty:
            # Show all tabs
            return
        
        # Check which sections have data
        has_hosting = any([
            self.current_client.hosting_service,
            self.current_client.hosting_link,
            self.current_client.hosting_login,
            self.current_client.hosting_password,
            self.current_client.hosting_notes
        ])
        
        has_database = any([
            self.current_client.db_username,
            self.current_client.db_name,
            self.current_client.db_password
        ])
        
        has_website = any([
            self.current_client.domain,
            self.current_client.admin_panel_link,
            self.current_client.admin_panel_login,
            self.current_client.admin_panel_password,
            getattr(self.current_client, 'github_repo', '')
        ])
        
        # Get all tabs
        tabs = []
        tab_count = self.notebook.index("end")
        
        for i in range(tab_count):
            tab_id = self.notebook.tabs()[i]
            tabs.append(tab_id)
        
        # Show/hide tabs based on data
        if not has_hosting and len(tabs) > 0:
            try:
                self.notebook.hide(tabs[0])  # Hosting tab
            except:
                pass
        elif has_hosting and len(tabs) > 0:
            try:
                self.notebook.add(tabs[0])  # Show hosting tab
            except:
                pass
        
        if not has_database and len(tabs) > 1:
            try:
                self.notebook.hide(tabs[1])  # Database tab
            except:
                pass
        elif has_database and len(tabs) > 1:
            try:
                self.notebook.add(tabs[1])  # Show database tab
            except:
                pass
        
        if not has_website and len(tabs) > 2:
            try:
                self.notebook.hide(tabs[2])  # Website tab
            except:
                pass
        elif has_website and len(tabs) > 2:
            try:
                self.notebook.add(tabs[2])  # Show website tab
            except:
                pass
    
    def show_settings(self):
        """Show settings dialog"""
        show_settings_dialog(self.root)
    
    def show_about(self):
        """Show about dialog"""
        about_text = f"""
{Config.APP_TITLE}
Version {Config.VERSION}

{Config.DESCRIPTION}

A secure, modern application for managing client data including hosting, database, and website information.

Features:
• Secure encryption of sensitive data
• Modern, intuitive interface
• Quick clipboard copying
• Search and filter functionality
• Cross-platform compatibility
"""
        messagebox.showinfo("About", about_text)
    
    def on_closing(self):
        """Handle application closing"""
        try:
            self.db_manager.close()
        except:
            pass
        self.root.quit()
        self.root.destroy()


def main():
    # Create the main window with modern theme
    root = ttk.Window(themename="cosmo")
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
