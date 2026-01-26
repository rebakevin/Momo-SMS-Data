import json
import re
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

from api.docs import DOC_ROUTES
from api.routes import ROUTES as APP_ROUTES
from api.service import SMSTransactionsService

# Merge routes from app and docs
ROUTES = {}
for source in [APP_ROUTES, DOC_ROUTES]:
    for method, paths in source.items():
        if method not in ROUTES:
            ROUTES[method] = {}
        ROUTES[method].update(paths)


class SMSTransactionsController(BaseHTTPRequestHandler):
    
    service = SMSTransactionsService()
    
    def _match_route(self, method, path):
        routes = ROUTES.get(method, {})
        
        if path in routes:
            return routes[path], {}
        
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
        path = urlparse(self.path).path
        
        handler_func, params = self._match_route('DELETE', path)
        if handler_func:
            if params:
                handler_func(self, **params)
            else:
                handler_func(self)
        else:
            self._send_error_response(404, "Route not found")
