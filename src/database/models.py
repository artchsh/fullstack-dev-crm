from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional, Dict, Any

# Create the declarative base
Base = declarative_base()


class ClientData(Base):
    """SQLAlchemy model for client data"""
    __tablename__ = 'clients'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Basic client info
    name = Column(String(255), nullable=False, index=True)
    
    # Hosting information
    hosting_service = Column(String(255))
    hosting_link = Column(String(500))
    hosting_login = Column(String(255))
    hosting_password = Column(Text)  # Encrypted
    hosting_notes = Column(Text)
    
    # Database information
    db_username = Column(String(255))
    db_name = Column(String(255))
    db_password = Column(Text)  # Encrypted
    
    # Website information
    domain = Column(String(255), index=True)
    admin_panel_link = Column(String(500))
    admin_panel_login = Column(String(255))
    admin_panel_password = Column(Text)  # Encrypted
    github_repo = Column(String(500))  # GitHub repository link
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __init__(self, name: str = "", hosting_service: str = "", hosting_link: str = "",
                 hosting_login: str = "", hosting_password: str = "", hosting_notes: str = "",
                 db_username: str = "", db_name: str = "", db_password: str = "",
                 domain: str = "", admin_panel_link: str = "", admin_panel_login: str = "",
                 admin_panel_password: str = "", github_repo: str = "", **kwargs):
        self.name = name
        self.hosting_service = hosting_service
        self.hosting_link = hosting_link
        self.hosting_login = hosting_login
        self.hosting_password = hosting_password
        self.hosting_notes = hosting_notes
        self.db_username = db_username
        self.db_name = db_name
        self.db_password = db_password
        self.domain = domain
        self.admin_panel_link = admin_panel_link
        self.admin_panel_login = admin_panel_login
        self.admin_panel_password = admin_panel_password
        self.github_repo = github_repo
    
    def __repr__(self):
        return f"<ClientData(id={self.id}, name='{self.name}', domain='{self.domain}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the client data to a dictionary"""
        return {
            'client_id': self.id,
            'name': self.name,
            'hosting_service': self.hosting_service or '',
            'hosting_link': self.hosting_link or '',
            'hosting_login': self.hosting_login or '',
            'hosting_password': self.hosting_password or '',
            'hosting_notes': self.hosting_notes or '',
            'db_username': self.db_username or '',
            'db_name': self.db_name or '',
            'db_password': self.db_password or '',
            'domain': self.domain or '',
            'admin_panel_link': self.admin_panel_link or '',
            'admin_panel_login': self.admin_panel_login or '',
            'admin_panel_password': self.admin_panel_password or '',
            'github_repo': self.github_repo or '',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClientData':
        """Create a ClientData instance from a dictionary"""
        # Remove client_id from data as SQLAlchemy handles the id separately
        data_copy = data.copy()
        data_copy.pop('client_id', None)
        data_copy.pop('created_at', None)
        data_copy.pop('updated_at', None)
        
        return cls(**data_copy)
    
    def format_for_clipboard(self, include_empty_sections: bool = False) -> str:
        """Format the client data for human-readable clipboard copying"""
        sections = []
        
        # Check if hosting section has data
        hosting_fields = [
            self.hosting_service, self.hosting_link, self.hosting_login, 
            self.hosting_password, self.hosting_notes
        ]
        has_hosting_data = any(field for field in hosting_fields if field)
        
        # Check if database section has data
        database_fields = [self.db_username, self.db_name, self.db_password]
        has_database_data = any(field for field in database_fields if field)
        
        # Check if website section has data
        website_fields = [
            self.domain, self.admin_panel_link, self.admin_panel_login,
            self.admin_panel_password, self.github_repo
        ]
        has_website_data = any(field for field in website_fields if field)
        
        # Add hosting section if it has data or if including empty sections
        if has_hosting_data or include_empty_sections:
            hosting_section = """HOSTING INFORMATION:
- Service: {0}
- Link: {1}
- Login/Email: {2}
- Password: {3}
- Notes: {4}""".format(
                self.hosting_service or 'N/A',
                self.hosting_link or 'N/A', 
                self.hosting_login or 'N/A',
                self.hosting_password or 'N/A',
                self.hosting_notes or 'N/A'
            )
            sections.append(hosting_section)
        
        # Add database section if it has data or if including empty sections
        if has_database_data or include_empty_sections:
            database_section = """DATABASE INFORMATION:
- Username: {0}
- Database Name: {1}
- Password: {2}""".format(
                self.db_username or 'N/A',
                self.db_name or 'N/A',
                self.db_password or 'N/A'
            )
            sections.append(database_section)
        
        # Add website section if it has data or if including empty sections
        if has_website_data or include_empty_sections:
            website_section = """WEBSITE INFORMATION:
- Domain: {0}
- Admin Panel Link: {1}
- Admin Panel Login: {2}
- Admin Panel Password: {3}
- GitHub Repository: {4}""".format(
                self.domain or 'N/A',
                self.admin_panel_link or 'N/A',
                self.admin_panel_login or 'N/A',
                self.admin_panel_password or 'N/A',
                self.github_repo or 'N/A'
            )
            sections.append(website_section)
        
        # Build the final string
        content = f"CLIENT: {self.name}\n" + "=" * 40 + "\n"
        
        if sections:
            content += "\n" + "\n\n".join(sections) + "\n"
        else:
            content += "\nNo data available for this client.\n"
        
        content += "\n" + "=" * 40 + "\n"
        content += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return content
    
    def update_from_dict(self, data: Dict[str, Any]):
        """Update instance from dictionary data"""
        for key, value in data.items():
            if hasattr(self, key) and key not in ['id', 'created_at']:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()


def create_database_engine(database_url: str):
    """Create and configure database engine"""
    engine = create_engine(
        database_url,
        echo=False,  # Set to True for SQL debugging
        pool_recycle=3600,  # Recycle connections every hour
        connect_args={'check_same_thread': False} if 'sqlite' in database_url else {}
    )
    return engine


def create_session_factory(engine):
    """Create session factory"""
    return sessionmaker(bind=engine)


def init_database(database_url: str):
    """Initialize database and create all tables"""
    engine = create_database_engine(database_url)
    Base.metadata.create_all(engine)
    return engine, create_session_factory(engine)