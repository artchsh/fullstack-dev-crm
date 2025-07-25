from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, and_
from typing import List, Optional
from datetime import datetime
from contextlib import contextmanager

from utils.encryption import EncryptionManager
from .models import ClientData, init_database
from config.settings import Config


class DatabaseManager:
    def __init__(self, database_url: str = None):
        """Initialize database manager with SQLAlchemy"""
        self.database_url = database_url or f"sqlite:///{Config.get_database_path()}"
        self.encryption_manager = EncryptionManager()
        
        # Initialize database
        self.engine, self.session_factory = init_database(self.database_url)
    
    @contextmanager
    def get_session(self):
        """Context manager for database sessions"""
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def _encrypt_sensitive_fields(self, client: ClientData) -> None:
        """Encrypt sensitive fields in place"""
        if client.hosting_password:
            client.hosting_password = self.encryption_manager.encrypt(client.hosting_password)
        if client.db_password:
            client.db_password = self.encryption_manager.encrypt(client.db_password)
        if client.admin_panel_password:
            client.admin_panel_password = self.encryption_manager.encrypt(client.admin_panel_password)
    
    def _decrypt_sensitive_fields(self, client: ClientData) -> None:
        """Decrypt sensitive fields in place"""
        if client.hosting_password:
            client.hosting_password = self.encryption_manager.decrypt(client.hosting_password)
        if client.db_password:
            client.db_password = self.encryption_manager.decrypt(client.db_password)
        if client.admin_panel_password:
            client.admin_panel_password = self.encryption_manager.decrypt(client.admin_panel_password)
    
    def insert_client(self, client_data: ClientData) -> int:
        """Insert a new client record"""
        try:
            with self.get_session() as session:
                # Create new client instance
                new_client = ClientData(
                    name=client_data.name,
                    hosting_service=client_data.hosting_service,
                    hosting_link=client_data.hosting_link,
                    hosting_login=client_data.hosting_login,
                    hosting_password=client_data.hosting_password,
                    hosting_notes=client_data.hosting_notes,
                    db_username=client_data.db_username,
                    db_name=client_data.db_name,
                    db_password=client_data.db_password,
                    domain=client_data.domain,
                    admin_panel_link=client_data.admin_panel_link,
                    admin_panel_login=client_data.admin_panel_login,
                    admin_panel_password=client_data.admin_panel_password
                )
                
                # Encrypt sensitive fields
                self._encrypt_sensitive_fields(new_client)
                
                # Add to session and flush to get ID
                session.add(new_client)
                session.flush()
                
                return new_client.id
                
        except SQLAlchemyError as e:
            print(f"Database error inserting client: {e}")
            raise
        except Exception as e:
            print(f"Error inserting client: {e}")
            raise
    
    def get_all_clients(self) -> List[ClientData]:
        """Retrieve all client records"""
        try:
            with self.get_session() as session:
                clients = session.query(ClientData).order_by(ClientData.name).all()
                
                # Decrypt sensitive fields for each client
                result_clients = []
                for client in clients:
                    # Create a detached copy to avoid session issues
                    client_copy = ClientData(
                        name=client.name,
                        hosting_service=client.hosting_service,
                        hosting_link=client.hosting_link,
                        hosting_login=client.hosting_login,
                        hosting_password=client.hosting_password,
                        hosting_notes=client.hosting_notes,
                        db_username=client.db_username,
                        db_name=client.db_name,
                        db_password=client.db_password,
                        domain=client.domain,
                        admin_panel_link=client.admin_panel_link,
                        admin_panel_login=client.admin_panel_login,
                        admin_panel_password=client.admin_panel_password
                    )
                    client_copy.id = client.id
                    client_copy.created_at = client.created_at
                    client_copy.updated_at = client.updated_at
                    
                    try:
                        self._decrypt_sensitive_fields(client_copy)
                        result_clients.append(client_copy)
                    except Exception as e:
                        print(f"Error decrypting client {client.id}: {e}")
                        # Add client with encrypted data as fallback
                        result_clients.append(client_copy)
                
                return result_clients
                
        except SQLAlchemyError as e:
            print(f"Database error retrieving clients: {e}")
            return []
        except Exception as e:
            print(f"Error retrieving clients: {e}")
            return []
    
    def get_client_by_id(self, client_id: int) -> Optional[ClientData]:
        """Retrieve a specific client by ID"""
        try:
            with self.get_session() as session:
                client = session.query(ClientData).filter(ClientData.id == client_id).first()
                
                if client:
                    # Create a detached copy
                    client_copy = ClientData(
                        name=client.name,
                        hosting_service=client.hosting_service,
                        hosting_link=client.hosting_link,
                        hosting_login=client.hosting_login,
                        hosting_password=client.hosting_password,
                        hosting_notes=client.hosting_notes,
                        db_username=client.db_username,
                        db_name=client.db_name,
                        db_password=client.db_password,
                        domain=client.domain,
                        admin_panel_link=client.admin_panel_link,
                        admin_panel_login=client.admin_panel_login,
                        admin_panel_password=client.admin_panel_password
                    )
                    client_copy.id = client.id
                    client_copy.created_at = client.created_at
                    client_copy.updated_at = client.updated_at
                    
                    try:
                        self._decrypt_sensitive_fields(client_copy)
                    except Exception as e:
                        print(f"Error decrypting client {client_id}: {e}")
                    
                    return client_copy
                
                return None
                
        except SQLAlchemyError as e:
            print(f"Database error retrieving client {client_id}: {e}")
            return None
        except Exception as e:
            print(f"Error retrieving client {client_id}: {e}")
            return None
    
    def update_client(self, client_data: ClientData) -> bool:
        """Update an existing client record"""
        if not client_data.id:
            return False
        
        try:
            with self.get_session() as session:
                # Get existing client
                existing_client = session.query(ClientData).filter(ClientData.id == client_data.id).first()
                
                if not existing_client:
                    return False
                
                # Update fields
                existing_client.name = client_data.name
                existing_client.hosting_service = client_data.hosting_service
                existing_client.hosting_link = client_data.hosting_link
                existing_client.hosting_login = client_data.hosting_login
                existing_client.hosting_password = client_data.hosting_password
                existing_client.hosting_notes = client_data.hosting_notes
                existing_client.db_username = client_data.db_username
                existing_client.db_name = client_data.db_name
                existing_client.db_password = client_data.db_password
                existing_client.domain = client_data.domain
                existing_client.admin_panel_link = client_data.admin_panel_link
                existing_client.admin_panel_login = client_data.admin_panel_login
                existing_client.admin_panel_password = client_data.admin_panel_password
                existing_client.updated_at = datetime.utcnow()
                
                # Encrypt sensitive fields
                self._encrypt_sensitive_fields(existing_client)
                
                return True
                
        except SQLAlchemyError as e:
            print(f"Database error updating client: {e}")
            return False
        except Exception as e:
            print(f"Error updating client: {e}")
            return False
    
    def delete_client(self, client_id: int) -> bool:
        """Delete a client record"""
        try:
            with self.get_session() as session:
                client = session.query(ClientData).filter(ClientData.id == client_id).first()
                
                if client:
                    session.delete(client)
                    return True
                
                return False
                
        except SQLAlchemyError as e:
            print(f"Database error deleting client: {e}")
            return False
        except Exception as e:
            print(f"Error deleting client: {e}")
            return False
    
    def search_clients(self, search_term: str) -> List[ClientData]:
        """Search for clients by name or domain"""
        try:
            with self.get_session() as session:
                # Case-insensitive search
                search_pattern = f"%{search_term}%"
                clients = session.query(ClientData).filter(
                    or_(
                        ClientData.name.ilike(search_pattern),
                        ClientData.domain.ilike(search_pattern),
                        ClientData.hosting_service.ilike(search_pattern)
                    )
                ).order_by(ClientData.name).all()
                
                # Decrypt sensitive fields for each client
                result_clients = []
                for client in clients:
                    # Create a detached copy
                    client_copy = ClientData(
                        name=client.name,
                        hosting_service=client.hosting_service,
                        hosting_link=client.hosting_link,
                        hosting_login=client.hosting_login,
                        hosting_password=client.hosting_password,
                        hosting_notes=client.hosting_notes,
                        db_username=client.db_username,
                        db_name=client.db_name,
                        db_password=client.db_password,
                        domain=client.domain,
                        admin_panel_link=client.admin_panel_link,
                        admin_panel_login=client.admin_panel_login,
                        admin_panel_password=client.admin_panel_password
                    )
                    client_copy.id = client.id
                    client_copy.created_at = client.created_at
                    client_copy.updated_at = client.updated_at
                    
                    try:
                        self._decrypt_sensitive_fields(client_copy)
                        result_clients.append(client_copy)
                    except Exception as e:
                        print(f"Error decrypting client {client.id}: {e}")
                        result_clients.append(client_copy)
                
                return result_clients
                
        except SQLAlchemyError as e:
            print(f"Database error searching clients: {e}")
            return []
        except Exception as e:
            print(f"Error searching clients: {e}")
            return []
    
    def get_client_count(self) -> int:
        """Get total number of clients"""
        try:
            with self.get_session() as session:
                return session.query(ClientData).count()
        except Exception:
            return 0
    
    def close(self):
        """Close database connections"""
        if hasattr(self, 'engine'):
            self.engine.dispose()