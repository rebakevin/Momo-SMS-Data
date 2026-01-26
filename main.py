from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import re
from urllib.parse import urlparse
from api.routes import ROUTES
from api.service import SMSTransactionsService


class SMSTransactionsHandler(BaseHTTPRequestHandler):
    
    # Initialize service instance for transaction handling
    service = SMSTransactionsService()
    
    def _match_route(self, method, path):
        """Match path against routes with parameter support"""
        routes = ROUTES.get(method, {})
        
        # First try exact match
        if path in routes:
            return routes[path], {}
        
        # Try pattern matching for parameterized routes
        for route_pattern, handler in routes.items():
            if ':' in route_pattern:
                # Convert route pattern to regex
                # /transactions/:id -> /transactions/([^/]+)
                regex_pattern = re.sub(r':(\w+)', r'([^/]+)', route_pattern)
                regex_pattern = '^' + regex_pattern + '$'
                
                match = re.match(regex_pattern, path)
                if match:
                    # Extract parameter names and values
                    param_names = re.findall(r':(\w+)', route_pattern)
                    params = dict(zip(param_names, match.groups()))
                    return handler, params
        
        return None, {}
    
    def _send_error_response(self, status_code, message):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')

        if status_code == 401:
            self.send_header('WWW-Authenticate', 'Basic realm="Momo API"')
        
        self.end_headers()
        response = {"error": message}
        self.wfile.write(json.dumps(response).encode())

    def do_GET(self):
        """Handle GET requests"""
        path = urlparse(self.path).path
        
        handler_func, params = self._match_route('GET', path)
        if handler_func:
            if params:
                handler_func(self, **params)
            else:
                handler_func(self)
        else:
            self._send_error_response(404, "Route not found")
    
    def do_POST(self):
        """Handle POST requests"""
        path = urlparse(self.path).path
        
        handler_func, params = self._match_route('POST', path)
        if handler_func:
            if params:
                handler_func(self, **params)
            else:
                handler_func(self)
        else:
            self._send_error_response(404, "Route not found")
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        path = urlparse(self.path).path
        
        handler_func, params = self._match_route('DELETE', path)
        if handler_func:
            if params:
                handler_func(self, **params)
            else:
                handler_func(self)
        else:
            self._send_error_response(404, "Route not found")


if __name__ == "__main__":
    port = 8000
    server_address = ('', port)
    httpd = HTTPServer(server_address, SMSTransactionsHandler)
    print(f"Server running on http://localhost:{port}")
    print(f"API Documentation: http://localhost:{port}/api-docs")
    print(f"OpenAPI Spec: http://localhost:{port}/openapi.json")
    print("Press Ctrl+C to stop the server")
    httpd.serve_forever()