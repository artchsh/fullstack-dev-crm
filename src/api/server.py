from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time
from typing import Optional
from database.db_manager import DatabaseManager
from config.app_settings import app_settings
import logging


class ClientDataAPI:
    """REST API server for client data management"""
    
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for web access
        self.db_manager = None
        self.server_thread = None
        self.is_running = False
        
        # Configure logging
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        
        self.setup_routes()
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            if not self._verify_access_key():
                return jsonify({"error": "Unauthorized"}), 401
            return jsonify({"status": "healthy", "timestamp": time.time()})
        
        @self.app.route('/api/clients', methods=['GET'])
        def get_clients():
            """Get all clients"""
            if not self._verify_access_key():
                return jsonify({"error": "Unauthorized"}), 401
            
            try:
                clients = self.db_manager.get_all_clients()
                return jsonify({
                    "clients": [client.to_dict() for client in clients],
                    "count": len(clients)
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/clients/<int:client_id>', methods=['GET'])
        def get_client(client_id):
            """Get specific client by ID"""
            if not self._verify_access_key():
                return jsonify({"error": "Unauthorized"}), 401
            
            try:
                client = self.db_manager.get_client_by_id(client_id)
                if client:
                    return jsonify(client.to_dict())
                else:
                    return jsonify({"error": "Client not found"}), 404
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/clients', methods=['POST'])
        def create_client():
            """Create new client"""
            if not self._verify_access_key():
                return jsonify({"error": "Unauthorized"}), 401
            
            try:
                data = request.get_json()
                if not data or 'name' not in data:
                    return jsonify({"error": "Client name is required"}), 400
                
                client = self.db_manager.add_client(data)
                return jsonify({
                    "message": "Client created successfully",
                    "client": client.to_dict()
                }), 201
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/clients/<int:client_id>', methods=['PUT'])
        def update_client(client_id):
            """Update existing client"""
            if not self._verify_access_key():
                return jsonify({"error": "Unauthorized"}), 401
            
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"error": "No data provided"}), 400
                
                client = self.db_manager.update_client(client_id, data)
                if client:
                    return jsonify({
                        "message": "Client updated successfully",
                        "client": client.to_dict()
                    })
                else:
                    return jsonify({"error": "Client not found"}), 404
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/clients/<int:client_id>', methods=['DELETE'])
        def delete_client(client_id):
            """Delete client"""
            if not self._verify_access_key():
                return jsonify({"error": "Unauthorized"}), 401
            
            try:
                success = self.db_manager.delete_client(client_id)
                if success:
                    return jsonify({"message": "Client deleted successfully"})
                else:
                    return jsonify({"error": "Client not found"}), 404
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/search', methods=['GET'])
        def search_clients():
            """Search clients by name or domain"""
            if not self._verify_access_key():
                return jsonify({"error": "Unauthorized"}), 401
            
            try:
                query = request.args.get('q', '').strip()
                if not query:
                    return jsonify({"error": "Search query is required"}), 400
                
                clients = self.db_manager.search_clients(query)
                return jsonify({
                    "clients": [client.to_dict() for client in clients],
                    "count": len(clients),
                    "query": query
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    
    def _verify_access_key(self) -> bool:
        """Verify access key from request"""
        key = request.args.get('key') or request.headers.get('X-API-Key')
        return key == app_settings.get_api_key()
    
    def start_server(self, db_manager: DatabaseManager):
        """Start the API server"""
        if self.is_running:
            return False
        
        self.db_manager = db_manager
        host = app_settings.get_api_host()
        port = app_settings.get_api_port()
        
        def run_server():
            try:
                self.app.run(
                    host=host,
                    port=port,
                    debug=False,
                    use_reloader=False,
                    threaded=True
                )
            except Exception as e:
                print(f"API Server error: {e}")
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.is_running = True
        
        # Give server time to start
        time.sleep(0.5)
        return True
    
    def stop_server(self):
        """Stop the API server"""
        if self.is_running and self.server_thread:
            # Note: Flask development server doesn't have a clean shutdown method
            # In production, you'd use a proper WSGI server like Gunicorn
            self.is_running = False
            return True
        return False
    
    def get_api_info(self) -> dict:
        """Get API information"""
        if not self.is_running:
            return {"status": "stopped"}
        
        return {
            "status": "running",
            "host": app_settings.get_api_host(),
            "port": app_settings.get_api_port(),
            "access_key": app_settings.get_api_key(),
            "endpoints": [
                "GET /api/health",
                "GET /api/clients",
                "GET /api/clients/<id>",
                "POST /api/clients",
                "PUT /api/clients/<id>",
                "DELETE /api/clients/<id>",
                "GET /api/search?q=<query>"
            ]
        }


# Global API instance
api_server = ClientDataAPI()
